//go:build windows

package host

import "testing"

func TestWindowsCommandBoundary(t *testing.T) {
	for _, raw := range []string{"https://example.com/?x=a&b=1|2", "https://example.com/--user-data-dir=evil", "https://example.com/a%22b", "http://localhost:3000/"} {
		cmd := chromeCommand(`C:\Program Files\Google\Chrome\Application\chrome.exe`, raw)
		if cmd.Path != `C:\Program Files\Google\Chrome\Application\chrome.exe` || len(cmd.Args) != 2 || cmd.Args[1] != raw {
			t.Fatal("argument boundary changed")
		}
		if cmd.SysProcAttr.CreationFlags != 0x08000000|0x01000000 {
			t.Fatal("Chrome console/job lifetime flags changed")
		}
		if cmd.Stdin != nil || cmd.Stdout != nil || cmd.Stderr != nil {
			t.Fatal("browser inherited messaging pipes")
		}
	}
}
