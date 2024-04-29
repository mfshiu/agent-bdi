def my_function():
    # Some operations
    result_string = "Hello"
    result_number = 42
    return result_string, result_number

# Call the function and capture the outputs
output = my_function()

if output:
    print(f"Len of output: {len(output)}")    
    print(type(output))
    print(isinstance(output, tuple))
    topic, result = output
    print(topic)
    print(result)
    
