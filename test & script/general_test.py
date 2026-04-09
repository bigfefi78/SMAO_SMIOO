import win32com.client


prog_id = "SMAO.SMaoMain"

try:
    smao_main = win32com.client.Dispatch(prog_id)
    result = smao_main.Initialize("")
    if result < 0:
        print("Errore inizializzazione SMAO (Codice: {result})")
    else:
        smao_info = smao_main.Info
except Exception as ex:
    print(ex)
    import traceback

    traceback.print_exc()
print("=" * 20)
print("       SMAO MAIN")
print("=" * 20)
print(f"SmaoMain Drivers disponibili: {smao_main.Drivers}")
print(f"SmaoMain Driveres Count: {smao_main.DriversCount}")
print("=" * 20)
print("       SMAO INFO")
print("=" * 20)

print(f"SmaoInfo Drivers abilitati: {smao_info.Drivers}")
print(f"SmaoInfo Drivers count: {smao_info.DriversCount}")
print(f"SmaoInfo Sensors count: {smao_info.SensorsCount}")
for i in range(smao_info.DriversCount):
    driver = smao_info.Drivers[i]
    print(
        f"SmaoInfo Driver #{i + 1}: {driver}, Versione: {smao_info.DriverVersion(i + 1)}, Numero canali: {smao_info.ChannelsCount(i + 1)}"
    )

print(f"Channel del sensore: {smao_info.SensorChannel(68)}")
print(f"Driver del sensore: {smao_info.SensorDriver(68)}")