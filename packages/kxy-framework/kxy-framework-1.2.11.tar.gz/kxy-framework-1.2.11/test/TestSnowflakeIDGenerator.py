from kxy.framework.id_generator import SnowflakeIDGenerator


id_generator = SnowflakeIDGenerator()
generated_ids = set()

for _ in range(100000):
    new_id = id_generator.get_next_id()
    if new_id in generated_ids:
        print(f"Duplicate ID: {new_id}, len:{len(generated_ids)}")
        break
    generated_ids.add(new_id)