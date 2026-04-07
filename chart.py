import matplotlib.pyplot as plt

def generate_chart(data, symbol):
    plt.figure()
    plt.plot(data["Close"])
    plt.title(symbol)

    filename = f"{symbol}.png"
    plt.savefig(filename)
    plt.close()

    return filename