# TempCatcher, identify spam emails on clean domains.

## What is TempCatcher?
TempCatcher is a service which provides intelligence on temporary email addresses.

## Why use TempCatcher? 
Our service is the logical next step If you have exhausted all other solutions in your battle against spam (domain white-listing / blacklisting).

## How do i use TempCatcher?
Please refer to [quick start guide](https://github.com/tempcacher/tempcatcher/README.md#quick-start-guide)

## Where do you get your data?
We aggregate our data from a variety of known spam providers.

## Do you offer any paid services?
Yes, we offer a more simple "checks" api which allows you to send an email via http(s) and check if that is in our database.

For enterprise customers also provide intelligence on phone numbers as well.

if you are interested in these services please email contact@tempcatcher.com

---

# Quick Start guide
## 1) Install TempCatcher api.

`pip install tempcatcher`

## 2) Example code:
```python
from tempcatcher import *
t = TempCatcher()

email, status = t.check(input("Input email you would like to check: "), dns = True)

match status:
    case 0:
        print(f"Email: `{email}` was found in the tempcatcher data. (spam)")
    case 1:
        print(f"Email: `{email}` was not found in the tempcatcher data. (not spam)")
    case 2:
        print(f"Email was formatted incorrectly.")
    case 3:
        print(f"Email: `{email}` Could not find DNS MX record assocciated with domain")
    case _:
        print(f"How did we get here?")
del t # join update thread
```

# 3) Known Issues.
On windows / NT you may get a `UnicodeDecodeError` when trying to import tempcatcher,

the quickest solution is to add `-X utf8` to your command arguments,

but here is a [link](https://github.com/pallets/click/issues/2121#issuecomment-1691716436) to more in-depth analysis / help.
