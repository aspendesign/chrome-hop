package host

import (
	"bytes"
	"encoding/binary"
	"encoding/json"
	"errors"
	"io"
	"strings"
	"testing"
)

func TestURLs(t *testing.T) {
	valid := []string{
		"https://example.com/", "http://localhost:3000/", "http://127.0.0.1:8080/a",
		"https://[::1]:443/", "https://例え.テスト/道?x=é", "https://example.com/a%20b?q=a&b=1|2#x",
		"http://intranet/", "https://example.com/--user-data-dir=evil", "https://example.com/a%22b",
		"https://example.com/a'&b=1", "https://example.com/?x=$(test)&y=%25",
	}
	invalid := []string{
		"", "--incognito", "javascript:alert(1)", "file:///C:/a", "data:text/html,hi", "about:blank",
		`C:\Windows\cmd.exe`, "https:example.com", "https:///example.com", "//example.com/",
		"https://", "https://a b/", " https://example.com", "https://example.com\ncmd",
		"https://example.com\r", "https://example.com\x00", "https://example.com\u0085",
		"https://example.com/%00", "https://example.com/%0D%0a", "https://example.com/%7f",
		`https://example.com/"&calc`, `https://example.com\@evil.test`, "https://user:password@example.com/",
		"https://@example.com/", "http://[not-ip]/", "http://[::1", "http://::1/", "http://[fe80::1%25eth0]/",
		"http://example.com:0/", "http://example.com:65536/", "http://example.com:abc/", "http://example.com:/",
		"http://-bad.test/", "http://a..test/", "http://a|b/", "http://a%2fb/", "https://example.com/%",
		"https://example.com/%xx", "HTTPS://example.com/", "https://example.com/" + strings.Repeat("x", MaxURL),
		"https://example.com/\ufffd", "https://example.com/" + string([]byte{0xff}),
	}
	for _, raw := range valid {
		if !ValidURL(raw) {
			t.Errorf("valid case rejected: %q", raw)
		}
	}
	for i, raw := range invalid {
		if ValidURL(raw) {
			t.Errorf("invalid case accepted: %d", i)
		}
	}
	base := "https://example.com/"
	if !ValidURL(base + strings.Repeat("x", MaxURL-len(base))) {
		t.Fatal("max URL rejected")
	}
}

func TestMessageShape(t *testing.T) {
	valid := []byte(`{"op":"open","url":"https://example.com/"}`)
	if u, ok := ParseMessage(valid); !ok || u != "https://example.com/" {
		t.Fatal("valid message failed")
	}
	cases := []string{
		`null`, `[]`, `"open"`, `{}`, `{"url":"https://example.com/"}`, `{"op":"open"}`,
		`{"op":"open","url":"https://example.com/","command":"calc.exe"}`,
		`{"op":"run","url":"https://example.com/"}`, `{"OP":"open","url":"https://example.com/"}`,
		`{"op":"open","op":"open","url":"https://example.com/"}`,
		`{"op":"open","url":"https://example.com/","url":"https://evil.test/"}`,
		`{"op":"open","url":null}`, `{"op":"open","url":123}`, `{"op":"open","url":{}}`,
		`{"op":"open","url":"https://example.com/\u0000"}`,
		`{"op":"open","url":"https://example.com/\ud800"}`,
		`{"op":"open","url":"https://example.com/"} {}`, `{"op":"open","url":"https://example.com/",}`,
		`{"op":"open","url":"https://example.com/"`, "\xff",
	}
	for i, c := range cases {
		if _, ok := ParseMessage([]byte(c)); ok {
			t.Errorf("invalid JSON case accepted: %d", i)
		}
	}
	if _, ok := ParseMessage(bytes.Repeat([]byte(" "), MaxFrame+1)); ok {
		t.Fatal("oversized body accepted")
	}
}

func frame(body []byte) []byte {
	var h [4]byte
	binary.LittleEndian.PutUint32(h[:], uint32(len(body)))
	return append(h[:], body...)
}

func decodeResponse(t *testing.T, data []byte) Response {
	t.Helper()
	if len(data) < 4 || int(binary.LittleEndian.Uint32(data[:4])) != len(data)-4 {
		t.Fatal("bad response framing")
	}
	var response Response
	if err := json.Unmarshal(data[4:], &response); err != nil {
		t.Fatal(err)
	}
	return response
}

func TestServe(t *testing.T) {
	body := []byte(`{"op":"open","url":"https://example.com/?token=TEST-PRIVATE"}`)
	good := frame(body)
	for _, code := range []string{"opened", "chrome_not_found", "launch_failed", "unexpected PRIVATE"} {
		var output bytes.Buffer
		count := 0
		if err := Serve(bytes.NewReader(append(append([]byte{}, good...), good...)), &output, func(u string) string {
			count++
			if u != "https://example.com/?token=TEST-PRIVATE" {
				t.Fatal("URL altered")
			}
			return code
		}); err != nil {
			t.Fatal(err)
		}
		r := decodeResponse(t, output.Bytes())
		if count != 1 || r.OK != (code == "opened") {
			t.Fatal("duplicate launch or bad status")
		}
		if strings.Contains(output.String(), "PRIVATE") {
			t.Fatal("input or OS error leaked")
		}
	}
	for i, input := range [][]byte{nil, {1}, {1, 0, 0}, {0, 0, 0, 0}, {255, 255, 255, 255}, {1, 128, 0, 0}, good[:len(good)-1], frame([]byte(`{}`)), frame([]byte{0xff})} {
		var output bytes.Buffer
		count := 0
		if err := Serve(bytes.NewReader(input), &output, func(string) string { count++; return "opened" }); err != nil {
			t.Fatal(err)
		}
		if count != 0 || decodeResponse(t, output.Bytes()).Code != "invalid_message" {
			t.Fatalf("bad frame accepted: %d", i)
		}
	}
}

type errorWriter struct{}

func (errorWriter) Write([]byte) (int, error) { return 0, errors.New("fixture") }
func TestOutputError(t *testing.T) {
	if WriteResponse(errorWriter{}, Response{}) == nil {
		t.Fatal("write error lost")
	}
}

func FuzzMessage(f *testing.F) {
	for _, s := range []string{`{"op":"open","url":"https://example.com/"}`, `{}`, `null`, string([]byte{0xff})} {
		f.Add([]byte(s))
	}
	f.Fuzz(func(t *testing.T, data []byte) {
		u, valid := ParseMessage(data)
		if valid && !ValidURL(u) {
			t.Fatal("parser accepted invalid URL")
		}
		var output bytes.Buffer
		count := 0
		if err := Serve(bytes.NewReader(frame(data)), &output, func(string) string { count++; return "opened" }); err != nil && err != io.EOF {
			t.Fatal(err)
		}
		if count > 1 || (count == 1) != valid {
			t.Fatal("serve/parser mismatch")
		}
		if len(output.Bytes()) > 100 {
			t.Fatal("unbounded response")
		}
	})
}
