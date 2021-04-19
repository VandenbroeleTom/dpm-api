package main

import (
  "log"
  "net/http"
  "encoding/json"
  "net/url"
)

type Code struct {
  Code string
}

func main() {
  client_id := "50808"
  client_secret := "dcd1be1ded9cde44bc9b117f39eedca3fd003e61"
  http.HandleFunc("/api/oauth/token", func (w http.ResponseWriter, r *http.Request) {
    var c Code
    json.NewDecoder(r.Body).Decode(&c)
    u, err := url.Parse("https://www.strava.com/oauth/token")
    q := u.Query()
    q.Set("client_id", client_id)
    q.Set("client_secret", client_secret)
    q.Set("code", c.Code)
    q.Set("grant_type", "authorization_code")
    u.RawQuery = q.Encode()
    if err != nil {
      json.NewEncoder(w).Encode(err)
      return
    }
    log.Println(u)
    resp, err := http.Post(u.String(), "application/json", nil)
    log.Println(resp)
    if err != nil {
      json.NewEncoder(w).Encode(err)
      return
    }
    json.NewEncoder(w).Encode(resp)
  })
  log.Fatal(http.ListenAndServe(":1235", nil))
}
