var latest_url = "https://api.github.com/repos/glidergeek/pysoar/releases/latest"

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

		document.getElementById("exec_mac").innerHTML = executable_name + " mac";
		document.getElementById("exec_mac").href = mac_url;

		// //latest windows cannot be built currently
		latest_windows = "v0.60.0";
		document.getElementById("exec_windows").innerHTML = latest_windows + " windows";
		console.log();
		document.getElementById("exec_windows").href = "https://github.com/GliderGeek/PySoar/releases/download/" + latest_windows + "/windows_" + latest_windows + ".zip";

		// //linux latest cannot be built currently
		latest_linux = "v0.56.3";
		document.getElementById("exec_linux").innerHTML = "v0.56.3 linux";
		document.getElementById("exec_linux").href = "https://github.com/GliderGeek/PySoar/releases/download/" + latest_linux + "/linux_" + latest_linux + ".zip";

	});
}