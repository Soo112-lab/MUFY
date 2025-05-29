def check_string(s):
    if s.startswith("the"):
        return "Yes"
    else:
        return "No"

str1 = "the"
str2 = "thumbs up"
str3 = "theathre can be boring"

print(check_string(str1))
print(check_string(str2))
print(check_string(str3))

