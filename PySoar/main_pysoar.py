from settingsClass import Settings
from competitionDay import CompetitionDay
from flightClass import Flight
from phasesClass import FlightPhases
from performanceClass import Performance
from importClass import SoaringSpotImport
from exportClass import ExcelExport
from Tkinter import Label, Tk, Button, Entry, W
from generalFunctions import url_format_correct
from generalFunctions import open_analysis_file
import time
import os

settings = Settings()


def run():
    root = Tk()
    root.resizable(0, 0)

    def url_check(event):
        checked_url = url_format_correct(url_entry.get())
        if checked_url == 'URL correct':
            url_status.configure(text=checked_url, foreground='green')
            url_status.update()
            start_pysoar()
        else:
            url_status.configure(text=checked_url, foreground='red')
            url_status.update()

    def go_bugform(event):
        import webbrowser

        form_url = settings.debug_form_url
        versionID = settings.pysoar_version_formID
        urlID = settings.competition_url_formID
        pysoar_version = settings.version

        comp_url = url_entry.get()

        complete_url = '%s?entry.%s=%s&entry.%s=%s' % (form_url, versionID, pysoar_version, urlID, comp_url)
        webbrowser.open(complete_url)

    def start_pysoar():
        settings = Settings()
        soaring_spot_info = SoaringSpotImport()
        competition_day = CompetitionDay()

        soaring_spot_info.load(url_entry.get())

        for index in range(len(soaring_spot_info.file_urls)):
            while not os.path.exists(soaring_spot_info.igc_directory + "/" + soaring_spot_info.file_names[index]):
                soaring_spot_info.download_flight(index)
                time.sleep(0.1)
            soaring_spot_info.flights_downloaded += 1
            download_progress.configure(text='Downloaded: ' + str(soaring_spot_info.flights_downloaded) + '/' + str(len(soaring_spot_info.file_names)))
            download_progress.update()

        if settings.debugging:
            soaring_spot_info.save(settings)

        for ii in range(len(soaring_spot_info.file_names)):
            file_name = soaring_spot_info.file_names[ii]
            ranking = soaring_spot_info.rankings[ii]
            competition_day.file_paths.append(soaring_spot_info.igc_directory + file_name)
            competition_day.flights.append(Flight(file_name, ranking))
            competition_day.flights[-1].read_igc(competition_day, soaring_spot_info)

        if competition_day.start_opening == 0:
            competition_day.ask_start_opening()

        competition_day.obtain_task_info()

        if settings.debugging:
            competition_day.save()

        for flight in competition_day.flights:

            print flight.file_name

            flight.determine_tsk_times(competition_day)
            flight.save(soaring_spot_info)

            flight.phases = FlightPhases(competition_day)
            flight.phases.determine_phases(settings, competition_day, flight)
            if settings.debugging:
                flight.phases.save(soaring_spot_info, flight)
            flight.phases.determine_point_statistics(flight, competition_day)

            flight.performance = Performance(competition_day, flight)
            flight.performance.determine_performance(flight, competition_day)

            soaring_spot_info.flights_analyzed += 1
            analysis_progress.configure(text='Analyzed: ' + str(soaring_spot_info.flights_analyzed) + '/' + str(len(soaring_spot_info.file_names)))
            analysis_progress.update()

        excel_sheet = ExcelExport(settings, competition_day)
        excel_sheet.write_file(competition_day, settings)

        analysis_done = Button(root, text='Excel produced', command=open_analysis_file)
        analysis_done.grid(row=6, column=0, pady=5)
        # analysis_done.configure(text='Excel produced!')

    title = Label(root, text=' PySoar', font=("Helvetica", 30))
    url_accompanying_text = Label(root, text='Give Soaringspot URL:')
    url_entry = Entry(root, width=60)
    url_confirmation = Button(root, text='ok')
    url_confirmation.bind('<Button-1>', url_check)
    url_status = Label(root, text='', foreground='red')
    download_progress = Label(root, text='Downloaded: ')
    analysis_progress = Label(root, text='Analyzed: ')
    report_problem = Button(root, text='Report problem')
    report_problem.bind('<Button-1>', go_bugform)
    root.bind('<Return>', url_check)

    title.grid(row=0, column=0)
    url_accompanying_text.grid(row=1, column=0, sticky=W)
    url_entry.grid(row=2, column=0)
    url_confirmation.grid(row=2, column=1)
    url_status.grid(row=3, column=0)
    download_progress.grid(row=4, column=0, pady=5)
    analysis_progress.grid(row=5, column=0, pady=5)
    report_problem.grid(row=7, column=0, sticky=W)

    root.mainloop()


if __name__ == '__main__':
    from main_pysoar import run

    run()
