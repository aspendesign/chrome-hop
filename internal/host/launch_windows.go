//go:build windows

package host

import (
	"os/exec"
	"syscall"
	"unsafe"
)

// All runtime dependencies are Windows system DLLs and the installed Chrome.
var shell32 = syscall.NewLazyDLL("shell32.dll")
var ole32 = syscall.NewLazyDLL("ole32.dll")

type guid struct {
	a    uint32
	b, c uint16
	d    [8]byte
}

var knownFolders = []guid{
	{0x905e63b6, 0xc1bf, 0x494e, [8]byte{0xb2, 0x9c, 0x65, 0xb7, 0x32, 0xd3, 0xd2, 0x1a}}, // ProgramFiles
	{0x7c5a40ef, 0xa0fb, 0x4bfc, [8]byte{0x87, 0x4a, 0xc0, 0xf2, 0xe0, 0xb9, 0xfa, 0x8e}}, // ProgramFilesX86
	{0xf1b32785, 0x6fba, 0x4fcf, [8]byte{0x9d, 0x55, 0x7b, 0x8e, 0x7f, 0x15, 0x70, 0x91}}, // LocalAppData
}

func ChromeRoots() []string {
	var roots []string
	get := shell32.NewProc("SHGetKnownFolderPath")
	free := ole32.NewProc("CoTaskMemFree")
	for i := range knownFolders {
		var ptr *uint16
		hresult, _, _ := get.Call(uintptr(unsafe.Pointer(&knownFolders[i])), 0, 0, uintptr(unsafe.Pointer(&ptr)))
		if hresult == 0 && ptr != nil {
			// Windows known-folder paths are bounded by the extended MAX_PATH.
			buf := unsafe.Slice(ptr, 32768)
			for n, c := range buf {
				if c == 0 {
					roots = append(roots, syscall.UTF16ToString(buf[:n]))
					break
				}
			}
			free.Call(uintptr(unsafe.Pointer(ptr)))
		}
	}
	return roots
}

func LaunchChrome(raw string) string {
	if !ValidURL(raw) {
		return "launch_failed"
	}
	path := FindChrome(ChromeRoots(), RegularChrome)
	if path == "" {
		return "chrome_not_found"
	}
	// URL is one discrete argument. Go performs Windows argument escaping.
	// No switches, shell, PATH search, inherited standard handles, or URL logging.
	cmd := chromeCommand(path, raw)
	if err := cmd.Start(); err != nil {
		return "launch_failed"
	}
	// Chrome may reuse an existing window or remain alive; never wait for it.
	if err := cmd.Process.Release(); err != nil {
		return "launch_failed"
	}
	return "opened"
}

func chromeCommand(path, raw string) *exec.Cmd {
	cmd := exec.Command(path, raw)
	// Chrome is a GUI executable: keep its intended window visible. The no-console
	// creation flag suppresses a console without requesting SW_HIDE for Chrome.
	// Mozilla kills the native messaging host's Windows Job after the response.
	// Chrome must break away from that Job to outlive this finite helper.
	cmd.SysProcAttr = &syscall.SysProcAttr{CreationFlags: 0x08000000 | 0x01000000}
	return cmd
}
