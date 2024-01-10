import pickle

with open("D:\\OneDrive\\圖片\\FXE86F3833C03D_000211.jpg", 'rb') as file:
    file_content = file.read()
print(f"file_content: {len(file_content)}")

# Example dictionary to serialize
data = {
    "name": "Alice", 
    "age": 30, 
    "city": "New York",
    "image": file_content
}

# Serializing the dictionary to bytes
serialized_data = pickle.dumps(data)

# Deserializing the bytes back to a dictionary
deserialized_data = pickle.loads(serialized_data)

# Displaying the results
# print("Serialized Data:", serialized_data)
# print("Deserialized Data:", deserialized_data)

print(f"image: {len(deserialized_data['image'])}")
with open("D:\\Temp\\xxx.jpg", 'wb') as file:
    file.write(deserialized_data["image"])
