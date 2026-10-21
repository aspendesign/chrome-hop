// Package host implements the one-message, one-URL native messaging boundary.
package host

import (
	"bytes"
	"encoding/binary"
	"encoding/json"
	"io"
	"net"
	"net/url"
	"strconv"
	"strings"
	"unicode"
	"unicode/utf8"
)

const (
	MaxFrame    = 32768
	MaxURL      = 16384
	ExtensionID = "chrome-hop@aspendesign.github.io"
	HostName    = "io.github.aspendesign.chrome_hop"
)

// Response never includes input, paths, OS errors, or browser output.
type Response struct {
	OK   bool   `json:"ok"`
	Code string `json:"code"`
}

type Launcher func(string) string

// Serve consumes exactly one bounded frame and emits exactly one response.
// Additional frames cannot cause additional launches. The caller supplies a
// deadline; EOF is not required after a valid frame (Firefox keeps stdin open).
func Serve(r io.Reader, w io.Writer, launch Launcher) error {
	response := Response{Code: "invalid_message"}
	var header [4]byte
	if _, err := io.ReadFull(r, header[:]); err == nil {
		size := binary.LittleEndian.Uint32(header[:])
		if size > 0 && size <= MaxFrame {
			body := make([]byte, size)
			if _, err = io.ReadFull(r, body); err == nil {
				if target, valid := ParseMessage(body); valid {
					code := launch(target)
					switch code {
					case "opened", "chrome_not_found", "launch_failed":
						response = Response{OK: code == "opened", Code: code}
					default:
						response.Code = "launch_failed"
					}
				}
			}
		}
	}
	return WriteResponse(w, response)
}

func WriteResponse(w io.Writer, response Response) error {
	body, err := json.Marshal(response)
	if err != nil {
		return err
	}
	var header [4]byte
	binary.LittleEndian.PutUint32(header[:], uint32(len(body)))
	_, err = io.Copy(w, bytes.NewReader(append(header[:], body...)))
	return err
}

// ParseMessage uses tokens so duplicate and case-variant keys are rejected too.
func ParseMessage(body []byte) (string, bool) {
	if len(body) == 0 || len(body) > MaxFrame || !utf8.Valid(body) {
		return "", false
	}
	d := json.NewDecoder(bytes.NewReader(body))
	start, err := d.Token()
	if err != nil || start != json.Delim('{') {
		return "", false
	}
	fields := make(map[string]string, 2)
	for d.More() {
		key, err := d.Token()
		if err != nil {
			return "", false
		}
		name, ok := key.(string)
		if !ok || (name != "op" && name != "url") {
			return "", false
		}
		if _, exists := fields[name]; exists {
			return "", false
		}
		var value string
		if err = d.Decode(&value); err != nil {
			return "", false
		}
		fields[name] = value
	}
	end, err := d.Token()
	if err != nil || end != json.Delim('}') {
		return "", false
	}
	if _, err = d.Token(); err != io.EOF {
		return "", false
	}
	if len(fields) != 2 || fields["op"] != "open" || !ValidURL(fields["url"]) {
		return "", false
	}
	return fields["url"], true
}

// ValidURL deliberately refuses ambiguous browser/parser inputs. It accepts
// localhost, IPv4/IPv6, internationalized domains, encoded text, and queries.
func ValidURL(raw string) bool {
	if len(raw) == 0 || len(raw) > MaxURL || !utf8.ValidString(raw) {
		return false
	}
	for _, c := range raw {
		if unicode.IsControl(c) || unicode.IsSpace(c) || c == '\\' || c == '"' || c == utf8.RuneError {
			return false
		}
	}
	for i := 0; i < len(raw); i++ {
		if raw[i] == '%' {
			if i+2 >= len(raw) {
				return false
			}
			n, err := strconv.ParseUint(raw[i+1:i+3], 16, 8)
			if err != nil || n < 32 || n == 127 {
				return false
			}
			i += 2
		}
	}
	u, err := url.Parse(raw)
	if err != nil || u.Opaque != "" || u.User != nil || u.Host == "" ||
		(u.Scheme != "http" && u.Scheme != "https") || !strings.HasPrefix(raw, u.Scheme+"://") {
		return false
	}
	host := u.Hostname()
	if host == "" || strings.ContainsAny(host, "%<>\"'`|^{}") {
		return false
	}
	if strings.Contains(host, ":") {
		if net.ParseIP(host) == nil || !strings.HasPrefix(u.Host, "[") {
			return false
		}
	} else {
		if strings.ContainsAny(host, "[]") {
			return false
		}
		for _, part := range strings.Split(strings.TrimSuffix(host, "."), ".") {
			if len(part) == 0 || len(part) > 63 || strings.HasPrefix(part, "-") || strings.HasSuffix(part, "-") {
				return false
			}
			for _, c := range part {
				if !unicode.IsLetter(c) && !unicode.IsDigit(c) && c != '-' && c != '_' {
					return false
				}
			}
		}
	}
	if strings.HasSuffix(u.Host, ":") {
		return false
	}
	if port := u.Port(); port != "" {
		n, err := strconv.Atoi(port)
		if err != nil || n < 1 || n > 65535 {
			return false
		}
	}
	return true
}
