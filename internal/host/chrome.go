package host

import (
	"os"
	"path/filepath"
	"strings"
)

// ChromeCandidates accepts OS known-folder results, never message input or PATH.
// Canary, beta, Chromium, shortcuts, and arbitrary App Paths values are excluded.
func ChromeCandidates(roots []string) []string {
	var paths []string
	seen := map[string]bool{}
	for _, root := range roots {
		if !filepath.IsAbs(root) {
			continue
		}
		path := filepath.Join(root, "Google", "Chrome", "Application", "chrome.exe")
		key := strings.ToLower(path)
		if !seen[key] {
			paths = append(paths, path)
			seen[key] = true
		}
	}
	return paths
}

// RegularChrome refuses links/junctions beneath the trusted known-folder root.
// A same-user malware process can already alter HKCU/native host registration;
// this helper is not a sandbox against an already-compromised Windows account.
func RegularChrome(path string) bool {
	if !filepath.IsAbs(path) || !strings.EqualFold(filepath.Base(path), "chrome.exe") {
		return false
	}
	current := path
	for i := 0; i < 4; i++ {
		info, err := os.Lstat(current)
		if err != nil || info.Mode()&(os.ModeSymlink|os.ModeIrregular) != 0 {
			return false
		}
		if i == 0 && (!info.Mode().IsRegular() || info.Size() == 0) {
			return false
		}
		if i > 0 && !info.IsDir() {
			return false
		}
		current = filepath.Dir(current)
	}
	return true
}

func FindChrome(roots []string, usable func(string) bool) string {
	for _, path := range ChromeCandidates(roots) {
		if usable(path) {
			return path
		}
	}
	return ""
}
