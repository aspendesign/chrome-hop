package host

import (
	"os"
	"path/filepath"
	"testing"
)

func TestDiscovery(t *testing.T) {
	root := t.TempDir()
	if got := ChromeCandidates([]string{"relative", root, root}); len(got) != 1 {
		t.Fatal("non-absolute or duplicate candidate")
	}
	if got := FindChrome([]string{root}, func(string) bool { return false }); got != "" {
		t.Fatal("missing chrome accepted")
	}
	path := ChromeCandidates([]string{root})[0]
	if RegularChrome(path) {
		t.Fatal("nonexistent executable accepted")
	}
	if err := os.MkdirAll(filepath.Dir(path), 0700); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, nil, 0600); err != nil {
		t.Fatal(err)
	}
	if RegularChrome(path) {
		t.Fatal("empty executable accepted")
	}
	if err := os.WriteFile(path, []byte("fixture"), 0600); err != nil {
		t.Fatal(err)
	}
	if !RegularChrome(path) || FindChrome([]string{root}, RegularChrome) != path {
		t.Fatal("fixed candidate not found")
	}
	if RegularChrome(filepath.Join(root, "calc.exe")) {
		t.Fatal("arbitrary executable accepted")
	}
	other := t.TempDir()
	link := filepath.Join(other, "Google")
	if err := os.Symlink(filepath.Join(root, "Google"), link); err == nil {
		if RegularChrome(ChromeCandidates([]string{other})[0]) {
			t.Fatal("linked path accepted")
		}
	} else {
		t.Log("symlink fixture unavailable under current Windows privilege")
	}
}
