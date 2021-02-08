import matplotlib.pyplot as plt


def simple_plot(coordinates: list):
    plt.plot([v[0] for v in coordinates], [v[1] for v in coordinates])
    plt.show()


def simple_plot_with_multiple_coordinates(read_coordinates: list, write_coordinates: list):
    plt.plot([v[0] for v in read_coordinates], [v[1] for v in read_coordinates], label='read_stats')
    plt.plot([v[0] for v in write_coordinates], [v[1] for v in write_coordinates], label='write_stats')
    plt.legend(loc='best')
    plt.show()
