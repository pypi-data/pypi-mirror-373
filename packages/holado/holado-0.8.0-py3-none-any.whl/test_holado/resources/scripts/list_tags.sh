grep -r --include="*.feature" -h "^\s*@[[:alnum:]._=:,;()-]\+" | tr "[ \r]" "\n" | sed '/^$/d' | sort | uniq -c

