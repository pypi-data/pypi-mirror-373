class Batcher:
    @staticmethod
    def create_batches(data: list, batch_size: int) -> list:
        if not isinstance(data, list):
            raise TypeError(f"'data' must be a list, got {type(data).__name__}")
        if not isinstance(batch_size, int) or batch_size <= 0:
            raise ValueError(
                f"'batch_size' must be a positive integer, got {batch_size}"
            )
        return [data[i : i + batch_size] for i in range(0, len(data), batch_size)]
