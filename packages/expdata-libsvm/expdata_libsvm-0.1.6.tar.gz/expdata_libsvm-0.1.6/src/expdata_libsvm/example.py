import read_data


if __name__ == "__main__":
    train_dataset, test_dataset, transform = read_data.main("w8a")
    print(train_dataset)