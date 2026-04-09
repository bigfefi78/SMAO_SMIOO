"""
Test minimale: Trova SOLO i canali attivi
Senza usare MultiChannels
"""

import win32com.client


def main():
    print("=" * 70)
    print("TEST: TROVA CANALI ATTIVI")
    print("=" * 70)
    
    try:
        # 1. CONNESSIONE
        print("\n[1] Connessione a SMAO...")
        smao_main = win32com.client.Dispatch("SMAO.SMaoMain")
        result = smao_main.Initialize("")
        
        if result < 0:
            print(f"    ✗ ERRORE: Inizializzazione fallita (code: {result})")
            return
        
        print("    ✓ Connesso")
        
        # 2. INFO
        info = smao_main.Info
        total_sensors = info.SensorsCount
        print(f"\n[2] Sensori totali configurati: {total_sensors}")
        
        # 3. SCANSIONE CON SINGLECHANNEL
        print("\n[3] Test di ogni canale con SingleChannel...")
        print("=" * 70)
        
        active_channels = []
        
        for sensor_idx in range(1, total_sensors + 1):
            driver_name = info.SensorDriver(sensor_idx)
            channel_number = info.SensorChannel(sensor_idx)
            
            try:
                # Crea SingleChannel
                single_ch = smao_main.NewSingleChannel()
                single_ch.Driver = driver_name
                single_ch.Channel = channel_number
                
                # Prova acquisizione
                single_ch.DoAcquisition()
                
                # Leggi status e valore
                ch_status = single_ch.ChannelStatus
                ch_value = single_ch.Value
                
                # ✅ Se status == 0 (CS_OK) è attivo
                if ch_status == 0:
                    active_channels.append({
                        'sensor_idx': sensor_idx,
                        'driver': driver_name,
                        'channel': channel_number,
                        'value': ch_value,
                        'status': ch_status
                    })
                    print(f"✓ Sensore {sensor_idx:2d}: {driver_name} Ch.{channel_number:2d} = {ch_value:10.3f} µm [ATTIVO]")
                else:
                    # Status diverso da 0 = NON attivo
                    print(f"○ Sensore {sensor_idx:2d}: {driver_name} Ch.{channel_number:2d} [Status={ch_status}]")
                
                # Rilascia oggetto
                del single_ch
                
            except Exception as ex:
                print(f"✗ Sensore {sensor_idx:2d}: {driver_name} Ch.{channel_number:2d} - ERRORE: {ex}")
        
        # 4. RIEPILOGO
        print("\n" + "=" * 70)
        print("RIEPILOGO")
        print("=" * 70)
        print(f"\nCanali totali:  {total_sensors}")
        print(f"Canali attivi:  {len(active_channels)}")
        print(f"Canali inattivi: {total_sensors - len(active_channels)}")
        
        if len(active_channels) > 0:
            print(f"\n{'='*70}")
            print("CANALI ATTIVI TROVATI:")
            print(f"{'='*70}")
            
            for ch in active_channels:
                print(f"\n  Sensore {ch['sensor_idx']}:")
                print(f"    Driver:  {ch['driver']}")
                print(f"    Channel: {ch['channel']}")
                print(f"    Valore:  {ch['value']:.3f} µm")
                print(f"    Status:  {ch['status']} (CS_OK)")
        else:
            print("\n⚠ NESSUN CANALE ATTIVO TROVATO!")
        
        print("\n" + "=" * 70)
        print("✅ TEST COMPLETATO")
        print("=" * 70)
        
    except Exception as ex:
        print(f"\n✗ ERRORE GENERALE: {ex}")
        import traceback
        traceback.print_exc()
    
    finally:
        try:
            info = None
            smao_main = None
            print("\n[Cleanup] Oggetti rilasciati")
        except:
            pass


if __name__ == "__main__":
    main()