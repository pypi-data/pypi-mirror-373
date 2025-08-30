# Unofficial CLI tool for ⌖ Hunter.how

# Usage examples

Set API key:
```
hunter-how set_api_key YOUR_KEY_HERE
```

Search for direcoty listings, output to file:
```
hunter-how search 'web.title="Index"' --page 1 --page-size 10 -o indexes.json
```

Parse from file, output ip:port to stdout:
```
hunter-how parse indexes.json --fields ip,port -d ":"
```


