c = open('index.html','r',encoding='utf-8').read()

# Extract the buildExportHTML function
start = c.find('function buildExportHTML')
end = c.find('\n// ===', start)
func = c[start:end]

# Count single quotes outside of string context is tricky
# Instead, let's find the return statement and check its structure
ret_start = func.find('return ')
# Everything from ret_start to the closing }; is the return value

# Find the closing of the function
# The function ends with: ;
# Let me find the semicolon that closes the return statement
# It should be: return '...';
# The string is very long - let me just check if it properly ends with ';
# by looking at the last few chars

# Find the last occurrence of '</html>\';' in the function
idx = func.rfind("</html>")
if idx > 0:
    tail = func[idx:idx+100]
    print("Export function tail:", repr(tail[:100]))
else:
    print("</html> not found in export function!")

# Also check the return statement structure
return_idx = func.find("return '")
print(f"\nreturn ' found at: {return_idx}")
# Find matching closing quote
# The return value is: return '<!DOCTYPE...';
# So it ends with ';
semicolon_after_return = func.find(';', return_idx)
print(f"First ; after return at: {semicolon_after_return}")
