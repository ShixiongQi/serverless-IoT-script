package main

import (
  "fmt"
  "log"
  "net/http"
  "os"
  "io/ioutil"
)

func handler(w http.ResponseWriter, r *http.Request) {
  log.Print("helloworld: received a request")
  target := os.Getenv("TARGET")
  if target == "" {
    target = "World"
  }
  
  body, _ := ioutil.ReadAll(r.Body)
//   fmt.Printf("request from generator: %v\n", string(body))
  if string(body) == "" {
	// fmt.Printf("body is nil\n")
	_, _ = http.Get("http://10.10.1.1:65432")
  } else {
	generator_ip := "http://10.10.1.1:" + string(body)
	// fmt.Printf("%s\n", generator_ip)
	_, _ = http.Get(generator_ip)
  }
  
//   if err != nil {
	// fmt.Printf("response from generator %v\n", resp)
//   }
  fmt.Fprintf(w, "Hello %s!\n", target)
}

func main() {
  log.Print("helloworld: starting server...")

  http.HandleFunc("/", handler)

  port := os.Getenv("PORT")
  if port == "" {
    port = "8080"
  }

  log.Printf("helloworld: listening on port %s", port)
  log.Fatal(http.ListenAndServe(fmt.Sprintf(":%s", port), nil))
}