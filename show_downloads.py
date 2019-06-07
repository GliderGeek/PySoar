import requests
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

api_url = 'https://api.github.com/repos/GliderGeek/PySoar/releases'


pysoar_releases = []  # List[{'name': <release_tag_name>, 'windows': 0, 'mac': 0, 'linux': 0}]
for release in requests.get(api_url).json():

    pysoar_release = {'name': release['tag_name']}
    for asset in release['assets']:
        if asset['name'].startswith('windows'):
            pysoar_release['windows'] = asset['download_count']
        if asset['name'].startswith('mac'):
            pysoar_release['mac'] = asset['download_count']
        if asset['name'].startswith('linux'):
            pysoar_release['linux'] = asset['download_count']

    pysoar_releases.append(pysoar_release)

print(pysoar_releases)


def get_plot_data(pysoar_releases):

    release_names = []
    windows_downloads = []
    mac_downloads = []
    linux_downloads = []
    for release in pysoar_releases:
        release_names.append(release['name'])
        windows_downloads.append(release.get('windows', 0))
        mac_downloads.append(release.get('mac', 0))
        linux_downloads.append(release.get('linux', 0))

    return release_names, windows_downloads, mac_downloads, linux_downloads


def plot_downloads_per_platform(windows_downloads, mac_downloads, linux_downloads, xtick_labels):
    
    ind = np.arange(len(xtick_labels))  # the x locations for the groups
    width = 0.2  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(ind - width, windows_downloads, width, label='Windows')
    rects2 = ax.bar(ind, mac_downloads, width, label='Mac')
    rects3 = ax.bar(ind + width, linux_downloads, width, label='Linux')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Downloads')
    ax.set_title('PySoar downloads by platform')
    ax.set_xticks(ind)
    ax.set_xticklabels(xtick_labels)
    ax.legend()

    def autolabel(rects, xpos='center'):
        """
        Attach a text label above each bar in *rects*, displaying its height.
        """

        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x(), height),
                        xytext=(0, 3),  # use 3 points offset
                        textcoords="offset points",  # in both directions
                        va='bottom')

    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)
    fig.tight_layout()
    plt.show()


release_names, windows_downloads, mac_downloads, linux_downloads = get_plot_data(pysoar_releases)
plot_downloads_per_platform(windows_downloads, mac_downloads, linux_downloads, release_names)
