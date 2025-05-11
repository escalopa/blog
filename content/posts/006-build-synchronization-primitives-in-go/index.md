---
title: "Don't Use Synchronization Primitives In Go — Build Them Yourself"
date: 2024-11-17
slug: "dont-use-synchronization-primitives-in-go-build-them-yourself"
summary: "Understand sync primitives deeper by building them."
categories: ["go"]
tags: ["concurrency", "synchronization"]
---

{{< lead >}}
Understand `sync` primitives better by building them yourself — but don't use them in production! 🚀
{{< /lead >}}

## DISCLAIMER ⚠️

This article is for **educational purposes only**.  
I don't recommend replacing the `sync` package structures in production.

The goal is to **strengthen your understanding** of the `sync` primitives and how they can be built using `chan`.

---

## Synchronization Primitives

Synchronization primitives control the behavior of applications during multithreaded execution.

In this article, we’ll cover three core structures from the `sync` package:

- Mutex
- RWMutex
- WaitGroup

For each, we will have:
- An example (buggy ➔ fixed)
- Method signature
- A full custom implementation using `chan`.

---

## Mutex

Mutex controls concurrent modifications of shared variables.

### Example

{{< highlight go >}}
import (
	"net/http"
	"strconv"
)

func main() {
	var counter int

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		counter++
		_, _ = w.Write([]byte(strconv.Itoa(counter)))
	})

	_ = http.ListenAndServe(":8080", nil)
}
{{< /highlight >}}

Looks innocent?  
Actually, **the counter can be corrupted** under high request concurrency!

---

### Solution

Use a `Mutex`:

{{< highlight go >}}
import (
	"net/http"
	"strconv"
	"sync"
)

func main() {
	var (
		mutex   sync.Mutex
		counter int
	)

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		mutex.Lock()
		defer mutex.Unlock()

		counter++
		_, _ = w.Write([]byte(strconv.Itoa(counter)))
	})

	_ = http.ListenAndServe(":8080", nil)
}
{{< /highlight >}}

---

### Signature
```go
type Mutex struct {}

func NewMutex() *Mutex {}
func (m *Mutex) Lock() {}
func (m *Mutex) Unlock() {}
```

---

### Custom Implementation

{{< highlight go >}}
type Mutex struct {
    channel chan struct{}
}

func NewMutex() *Mutex {
    return &Mutex{
        channel: make(chan struct{}, 1),
    }
}

func (m *Mutex) Lock() {
    m.channel <- struct{}{}
}

func (m *Mutex) Unlock() {
    select {
    case <-m.channel:
    default:
    panic("unlock of unlocked Mutex")
    }
}
{{< /highlight >}}

---

## RWMutex

`RWMutex` allows **multiple readers** but **only one writer**.

### Example

{{< highlight go >}}
type cache struct {
    storage map[string]interface{}
}

func NewCache() *cache {
    return &cache{storage: make(map[string]interface{})}
}

func (c *cache) Get(key string) interface{} {
    return c.storage[key]
}

func (c *cache) Set(key string, value interface{}) {
    c.storage[key] = value
}
{{< /highlight >}}

Concurrent writes will **corrupt** the `storage` map.

---

### Solution

Use `RWMutex`:

{{< highlight go >}}
import (
    "sync"
)

type cache struct {
    mutex   sync.RWMutex
    storage map[string]interface{}
}

func NewCache() *cache {
    return &cache{storage: make(map[string]interface{})}
}

func (c *cache) Get(key string) interface{} {
    c.mutex.RLock()
    defer c.mutex.RUnlock()
    return c.storage[key]
}

func (c *cache) Set(key string, value interface{}) {
    c.mutex.Lock()
    defer c.mutex.Unlock()
    c.storage[key] = value
}
{{< /highlight >}}

---

### Signature

```go
type RWMutex struct {}

func New() *RWMutex {}
func (rw *RWMutex) RLock() {}
func (rw *RWMutex) RUnlock() {}
func (rw *RWMutex) Lock() {}
func (rw *RWMutex) Unlock() {}
```

---

### Custom Implementation

{{< highlight go >}}
type RWMutex struct {
    counter int

	readChan  chan struct{}
	writeChan chan struct{}
	mutex     Mutex
}

func New() *RWMutex {
    return &RWMutex{
        readChan:  make(chan struct{}, 1),
        writeChan: make(chan struct{}, 1),
        mutex:     *NewMutex(),
    }
}

func (rw *RWMutex) RLock() {
    rw.mutex.Lock()
    defer rw.mutex.Unlock()

	if rw.counter == 0 {
		rw.readChan <- struct{}{}
	}
	rw.counter++
}

func (rw *RWMutex) RUnlock() {
    rw.mutex.Lock()
    defer rw.mutex.Unlock()

	if rw.counter == 0 {
		panic("unlock of unlocked RWMutex")
	}
	rw.counter--
	if rw.counter == 0 {
		<-rw.readChan
	}
}

func (rw *RWMutex) Lock() {
    rw.writeChan <- struct{}{}
    rw.readChan <- struct{}{}
}

func (rw *RWMutex) Unlock() {
    select {
    case <-rw.writeChan:
    default:
        panic("unlock of unlocked RWMutex")
    }
    <-rw.readChan
}
{{< /highlight >}}

---

## WaitGroup

`WaitGroup` waits for a collection of goroutines to finish.

### Example

{{< highlight go >}}
import (
    "math/rand/v2"
    "time"
)

func main() {
    for range 100 {
        go func() {
            time.Sleep(time.Duration(rand.IntN(10)) * time.Millisecond)
        }()
    }
}
{{< /highlight >}}

No waiting ➔ Main program may exit prematurely!

---

### Solution

{{< highlight go >}}
import (
    "math/rand/v2"
    "sync"
    "time"
)

func main() {
    wg := sync.WaitGroup{}

	for range 100 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			time.Sleep(time.Duration(rand.IntN(10)) * time.Millisecond)
		}()
	}

	wg.Wait()
}
{{< /highlight >}}

---

### Signature

```go
type WaitGroup struct {}

func New() *WaitGroup {}
func (wg *WaitGroup) Add(delta int) {}
func (wg *WaitGroup) Done() {}
func (wg *WaitGroup) Wait() {}
```

---

### Custom Implementation

{{< highlight go >}}
type WaitGroup struct {
    counter int
    channel chan struct{}
    mutex   Mutex
}

func New() *WaitGroup {
    return &WaitGroup{
        channel: make(chan struct{}, 1),
        mutex:   *NewMutex(),
    }
}

func (wg *WaitGroup) Add(delta int) {
    wg.mutex.Lock()
    defer wg.mutex.Unlock()

	if wg.counter == 0 && delta > 0 {
		wg.channel <- struct{}{}
	}

	wg.counter += delta

	if wg.counter < 0 {
		panic("negative WaitGroup counter")
	}

	if wg.counter == 0 {
		<-wg.channel
	}
}

func (wg *WaitGroup) Done() {
    wg.Add(-1)
}

func (wg *WaitGroup) Wait() {
    wg.channel <- struct{}{}
    <-wg.channel
}
{{< /highlight >}}

---

## Conclusion

If you made it this far, I hope you learned something new 💫.  
Stay tuned for more Go tips 🚀❤️‍🔥.
