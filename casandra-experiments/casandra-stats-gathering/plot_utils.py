import matplotlib.pyplot as plt
import seaborn as sns


def simple_plot(coordinates: list):
    plt.figure(figsize=(30, 15))
    plt.plot([v[0] for v in coordinates], [v[1] for v in coordinates])
    plt.show()


def simple_plot_dict(coordinates: dict):
    plt.figure(figsize=(15, 30))

    plt.plot(list(coordinates.values()), list(coordinates.keys()))
    plt.show()


def plot_multiple_dict(exp_name: str, all_diff: dict):
    plt.figure(figsize=(15, 15))

    for ip, diff in all_diff.items():
        plt.plot(list(diff.keys()), list(diff.values()), label='{ip}'.format(ip=ip))

    plt.legend(loc='best')
    plt.xlabel('version')
    plt.ylabel('delay ms')
    plt.title('Read per each version')

    plt.savefig('{exp}.png'.format(exp=exp_name), bbox_inches='tight')


def density_plot(exp_name: str, all_diff: dict):
    plt.figure(figsize=(15, 15))

    for ip, data in all_diff.items():
        print(len(data))
        sns.distplot(data, hist=False, kde=True,
                     kde_kws={'linewidth': 3},
                     label=ip)

    # Plot formatting
    plt.legend(prop={'size': 16}, title='IP')
    plt.title('Density Plot with Multiple Instances $Exp Id - ${id}'.format(id=exp_name))
    plt.xlabel('Delay (ms)')
    plt.ylabel('Density')
    # plt.xlim(0, 120)
    plt.show()


def plot_histogram(exp_name: str, all_diff: dict):
    names = []
    plot_data = []
    plt.figure(figsize=(15, 15))

    for ip, data in all_diff.items():
        plot_data.append(data)
        names.append(ip)

    plt.hist(plot_data, bins=50, label=names)

    plt.legend()
    plt.xlabel('Delay (ms)')
    plt.ylabel('Requests')
    plt.title('Side-by-Side Histogram with Multiple Instances ExpId - {id}'.format(id=exp_name))
    plt.show()
    # plt.savefig('{exp}.png'.format(exp=exp_name), bbox_inches='tight')



