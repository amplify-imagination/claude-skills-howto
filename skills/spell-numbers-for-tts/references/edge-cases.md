# Edge cases the converter does NOT handle

- **Years**: `2026` becomes "two thousand twenty-six", not "twenty twenty-six". Fix by hand.
- **Version strings**: `v4.8` would read as "four point eight" — strip versions first.
- **Phone / IDs**: long digit runs read as one big number. Leave these out of narration.
- **Ordinals**: `1st`, `2nd` are not converted.
