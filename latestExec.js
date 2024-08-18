var latest_url = "https://api.github.com/repos/glidergeek/pysoar/releases/latest"
var releases_url = "https://api.github.com/repos/GliderGeek/PySoar/releases"

function setExecutables(){

	var mac_url;
	var windows_url;
	var linux_url;
	var asset;
	var executable_name;
	var latest_windows;

	$.getJSON(latest_url).done(function (release) {

		executable_name = release.tag_name;

		for (asset_number in release.assets){

			asset = release.assets[asset_number];
			if (asset.name.substring(0, 3) == "mac") {
				mac_url = asset.browser_download_url;
			} else if (asset.name.substring(0, 7) == "windows") {
				windows_url = asset.browser_download_url;
			} else if (asset.name.substring(0, 5) == "linux") {
				linux_url = asset.browser_download_url;
			}	
		}

		document.getElementById("exec_mac").innerHTML = executable_name + " macOS 13";
		document.getElementById("exec_mac").href = mac_url;

		document.getElementById("exec_windows").innerHTML = executable_name + " windows";
		document.getElementById("exec_windows").href = windows_url;

		// //linux latest cannot be built currently
		latest_linux = "v0.56.3";
		document.getElementById("exec_linux").innerHTML = "v0.56.3 linux";
		document.getElementById("exec_linux").href = "https://github.com/GliderGeek/PySoar/releases/download/" + latest_linux + "/linux_" + latest_linux + ".zip";

	});
}

function setGraph(){


	var release_names = [];
	var release;
	var release_name;
	var mac_downloads = [];
	var windows_downloads = [];
	var linux_downloads = [];
	var total_downloads = 0
	var windows_download_count = 0
	var mac_download_count = 0
	var linux_download_count = 0

	$.getJSON(releases_url).done(function (releases) {

		for (release_number in releases){

			release = releases[release_number];
			release_name = release.tag_name;
			release_names.push(release_name);

			console.log(release_name)


			windows_download_count = 0
			mac_download_count = 0
			linux_download_count = 0
			for (asset_number in release.assets){
				asset = release.assets[asset_number];
				if (asset.name.startsWith('windows')){
					windows_download_count = asset.download_count
				} else if (asset.name.startsWith('mac')){
					mac_download_count = asset.download_count
				} else if (asset.name.startsWith('linux')){
					linux_download_count = asset.download_count
				}

			}

			windows_downloads.push(windows_download_count)
			mac_downloads.push(mac_download_count)
			linux_downloads.push(linux_download_count)
			total_downloads = total_downloads + (windows_download_count + mac_download_count + linux_download_count)
		}


		const ctx = document.getElementById('myChart');

const labels = release_names;
const data = {
  labels: labels,
  datasets: [
    {
      label: 'Linux',
      data: linux_downloads,
      backgroundColor: '#2cd6b4',
    },
    {
      label: 'Mac',
      data: mac_downloads,
      backgroundColor: '#d62c38',
    },
    {
      label: 'Windows',
      data: windows_downloads,
      backgroundColor: '#2ca3d6',
    },
  ]
};

	new Chart(ctx, {
	type: 'bar',
  data: data,
  options: {
    plugins: {
      title: {
        display: true,
        text: `PySoar downloads (${total_downloads} total)`
      },
    },
    responsive: true,
    scales: {
      x: {
        stacked: true,
      },
      y: {
        stacked: true
      }
    }
  }
	});



	});


	

}

