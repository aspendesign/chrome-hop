//go:build !windows

package host

func LaunchChrome(string) string { return "chrome_not_found" }
