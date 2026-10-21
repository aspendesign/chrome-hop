package main

import (
	"os"
	"time"

	"github.com/aspendesign/chrome-hop/internal/host"
)

func main() {
	// Browser sends a manifest path followed by the initiating Firefox add-on ID.
	// This is defense in depth, not authentication of other local processes.
	if len(os.Args) != 3 || os.Args[2] != host.ExtensionID {
		_ = host.WriteResponse(os.Stdout, host.Response{Code: "unauthorized"})
		return
	}
	// A partial frame can otherwise pin a host forever. No URL is retained/logged.
	timer := time.AfterFunc(10*time.Second, func() { os.Exit(1) })
	defer timer.Stop()
	if host.Serve(os.Stdin, os.Stdout, host.LaunchChrome) != nil {
		os.Exit(1)
	}
}
