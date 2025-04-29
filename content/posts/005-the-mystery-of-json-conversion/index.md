---
title: "The Mystery Of JSON Conversion From Float64 To Int64"
date: 2024-09-01
summary: "Why Go JSON Unmarshal turns int64 into float64 and how to fix it."
categories: ["go", "json"]
tags: ["debug"]
slug:  "the-mystery-of-json-conversion-from-float64-to-int64"
---

{{< lead >}}
Working with JSON seems simple — until you encounter some weird behavior from `Marshal` / `Unmarshal` functions.
{{< /lead >}}

## Problem 😨

It all started when I was trying to read the encoded payload from a JWT token.  
Here's a simplified example that demonstrates the issue:

{{< highlight go >}}
package main

import (
    "encoding/json"
    "fmt"
)

type User struct {
    ID      int64   `json:"id"`
    PostIDs []int64 `json:"post_ids"`
}

func main() {
    u := User{
        ID:      1,
        PostIDs: []int64{1, 2, 3},
    }

	b, err := json.Marshal(u)
	if err != nil {
		panic(err)
	}

	m := make(map[string]interface{})
	if err = json.Unmarshal(b, &m); err != nil {
		panic(err)
	}

	userID, ok := m["id"].(int64)
	fmt.Printf("id: %d\nOk:%t\n", userID, ok)

	fmt.Println() // splitter

	postIDs, ok := m["id"].([]int64)
	fmt.Printf("post_ids: %v\nOk:%t\n", postIDs, ok)
}
{{< /highlight >}}

Just marshaling and unmarshaling back our struct — so it’s expected to return the same values, right?

Unfortunately, the output is:

{{< highlight text >}}
id: 0
Ok:false

post_ids: []
Ok:false
{{< /highlight >}}

---

## Debug 🐞

I suspected the issue was with type conversion, so I printed the actual types:

{{< highlight go >}}
fmt.Printf("id: %T\n", m["id"])
fmt.Printf("post_ids: %T\n", m["post_ids"])
{{< /highlight >}}

And the output:

{{< highlight text >}}
id: float64
post_ids: []interface {}
{{< /highlight >}}

So `json.Unmarshal` parsed `int64` as `float64`, causing the mismatch.

---

## Solutions ✅

### 📃 Solution 01 (Hard Way)

Manually assert the types, keeping in mind that `[]interface{}` can't be directly casted to `[]float64`:

{{< highlight go >}}
// Parse UserID
userID, _ := m["id"].(float64)
fmt.Printf("id: %f\n", userID)

fmt.Println() // splitter

// Parse PostIDs
postIDsArr, _ := m["post_ids"].([]interface{})
postIDs := make([]int64, len(postIDsArr))
for i, v := range postIDsArr {
    // NOTICE: direct conversion to int64 won't work here!
    id, _ := v.(float64)
    postIDs[i] = int64(id)
}

fmt.Printf("post_ids: %v\n", postIDs)
{{< /highlight >}}

**Output:**

{{< highlight text >}}
id: 1.000000
post_ids: [1 2 3]
{{< /highlight >}}

---

### 📃 Solution 02 (Easy Way)

Just **marshal the map again** and unmarshal it into the struct:

{{< highlight go >}}
b, err = json.Marshal(m)
if err != nil {
    panic(err)
}

var u2 User
if err := json.Unmarshal(b, &u2); err != nil {
    panic(err)
}

fmt.Println(u2.ID)
fmt.Println(u2.PostIDs)
{{< /highlight >}}

Much simpler! ✅

---

## Which Solution is Better? 🤔

It **depends**:

- If you need to **read a single attribute**, doing all the marshaling/unmarshaling is overkill ➔ Solution 01.
- If you need **the whole object**, or **multiple attributes**, ➔ Solution 02 is cleaner and safer.

---

## Conclusion 🎉

That's it for today's article!

I hope you learned something new, my fellow gopher 🥰.
