"""
Translation strings for MSR605 Card Reader/Writer.
"""

# List of available language codes
LANGUAGES = ["en", "it"]

# Translation strings organized by language
TRANSLATIONS = {
    "en": {
        # Application
        "app_title": "MSR605 Card Reader/Writer v{version}",
        
        # Advanced Functions
        "adv_tab_decode": "Decode Card",
        "adv_tab_decrypt": "Decrypt Data",
        "adv_tab_visualization": "Visualization",
        "lbl_select_tracks": "Select Tracks to Decode:",
        "chk_track_1": "Track 1",
        "chk_track_2": "Track 2",
        "chk_track_3": "Track 3",
        "btn_decode_tracks": "Decode Selected Tracks",
        "grp_decoded_data": "Decoded Data",
        "grp_encryption_key": "Encryption Key",
        "lbl_key_hex": "Key (hex):",
        "placeholder_enter_key": "Enter encryption key...",
        "grp_algorithm": "Algorithm",
        "algo_aes256": "AES-256",
        "algo_aes192": "AES-192",
        "algo_aes128": "AES-128",
        "algo_des": "DES",
        "algo_3des": "3DES",
        "grp_data_decrypt": "Data to Decrypt",
        "placeholder_enter_data": "Enter data to decrypt or use 'Load Track Data'...",
        "btn_load_track": "Load Track Data",
        "btn_decrypt": "Decrypt",
        "lbl_decryption_results": "Decryption Results:",
        "lbl_loading_track": "Loading track data...",
        "lbl_no_track_data": "No track data available",
        "lbl_select_track_prompt": "Select track to load:",
        "lbl_processing": "Processing...",
        "lbl_decryption_complete": "Decryption complete",
        "lbl_decryption_failed": "Decryption failed",
        
        # Read Tab
        "btn_read_card": "Read Card",
        "read_card_tooltip": "Read data from a magnetic stripe card",
        "btn_advanced_functions": "Advanced Functions",
        "lbl_status_ready": "Ready to read card...",
        "no_visualizations_available": "No visualizations available. Read a card to see visualizations.",
        "no_data_available": "No data available",
        "processing_data": "Processing card data...",
        "viz_character_distribution_title": "Character Distribution",
        "viz_bit_pattern_title": "Bit Pattern",
        "viz_data_density_title": "Data Density",
        "viz_field_analysis_title": "Field Analysis",
        
        # Menu items
        "menu_file": "&File",
        "menu_database": "&Database",
        "menu_tools": "&Tools",
        "menu_help": "&Help",
        "menu_sponsor": "&Sponsor",
        "menu_view": "&View",
        "menu_voice": "&Voice",
        "menu_language": "&Language",
        "menu_enable_voice": "Enable &Voice Control",
        "menu_voice_help": "Voice Commands &Help",
        "menu_view_logs": "View &Logs",
        
        # File menu
        "menu_exit": "E&xit",
        "menu_exit_shortcut": "Ctrl+Q",
       
        # Database menu
        "menu_view_database": "&View Database",
        "menu_export_csv": "&Export to CSV",
        "menu_auto_save": "Autosave Read Cards",
        "menu_allow_duplicates": "Save Duplicate Cards",
        
        # Help menu
        "menu_help_contents": "&Help Contents",
        "menu_check_updates": "Check for &Updates",
        "menu_about": "&About",
        "menu_support": "&Support Project",
        
        # Tabs
        "tab_read": "Read Card",
        "tab_write": "Write Card",
        "tab_database": "Database",
        "tab_settings": "Settings",
        
        # Read tab
        "btn_read_card": "Read Card",
        "lbl_track_data": "Track Data",
        "lbl_status_ready": "Ready to read card...",
        "lbl_reading": "Reading card...",
        "lbl_read_success": "Card read successfully!",
        "lbl_read_error": "Error reading card",
        
        # Write tab
        "btn_write_card": "Write Card",
        "btn_clear_tracks": "Clear Tracks",
        "lbl_write_status_ready": "Ready to write card...",
        "lbl_writing": "Writing to card...",
        "lbl_write_success": "Card written successfully!",
        "lbl_write_error": "Error writing to card",
        "lbl_no_data": "No data to write",
        
        # Database tab
        "btn_refresh": "Refresh",
        "btn_export": "Export to CSV",
        "lbl_search": "Search:",
        "lbl_search_placeholder": "Search database...",
        "col_date": "Date",
        "col_track1": "Track 1",
        "col_track2": "Track 2",
        "col_track3": "Track 3",
        "col_notes": "Notes",
        "export_success": "Successfully exported {count} records to:\n{path}",
        "export_failed": "Failed to export database: {error}",
        
        # Settings tab
        "grp_connection": "Connection Settings",
        "grp_coercivity": "Coercivity",
        "grp_database": "Database Settings",
        "lbl_port": "Port:",
        "btn_connect": "Connect",
        "btn_disconnect": "Disconnect",
        "lbl_hi_coercivity": "High Coercivity (300 Oe)",
        "lbl_lo_coercivity": "Low Coercivity (300 Oe)",
        "lbl_auto_save": "Auto-save read cards to database",
        "lbl_allow_duplicates": "Allow duplicate cards in database",
        
        # Messages
        "msg_not_connected": "Please connect to the MSR605 first",
        "msg_connection_success": "Connected to {port}",
        "msg_connection_error": "Failed to connect to {port}: {error}",
        "msg_disconnected": "Disconnected",
        "msg_no_ports": "No port selected or no ports available",
        "msg_coercivity_set": "Set to {coercivity} coercivity",
        "msg_coercivity_error": "Failed to set coercivity: {error}",
        "msg_reset_error": "Failed to reset MSR605: {error}",
        "msg_import_error": "Failed to import module: {module}",
        "msg_database_error": "Database error: {error}",
        "msg_confirm_exit": "Are you sure you want to exit?",
        
        # Dialogs
        "dlg_about_title": "About MSR605 Card Reader",
        "dlg_help_title": "Help",
        "dlg_database_title": "Card Database",
        "dlg_export_title": "Export Database to CSV",
        "dlg_confirm_title": "Confirm",
        "dlg_error_title": "Error",
        "btn_ok": "OK",
        "btn_cancel": "Cancel",
        "btn_close": "Close",
        
        # Help text
        "help_content": """
        <h2>MSR605 Card Reader - Help</h2>
        
        <h3>Basic Usage:</h3>
        <ul>
            <li><b>Read Card</b>: Click the 'Read Card' button and swipe a card through the reader.</li>
            <li><b>Write Card</b>: Enter data in the track fields and click 'Write Card'.</li>
            <li><b>Clear Tracks</b>: Click 'Clear Tracks' to clear all track data.</li>
        </ul>
        
        <h3>Database Features:</h3>
        <ul>
            <li><b>View Database</b>: View all previously read cards in the database.</li>
            <li><b>Export to CSV</b>: Export the card database to a CSV file.</li>
            <li><b>Auto-save</b>: Toggle automatic saving of read cards to the database.</li>
            <li><b>Allow Duplicates</b>: Toggle whether to allow saving duplicate card data.</li>
        </ul>
        
        <h3>Advanced:</h3>
        <ul>
            <li><b>Coercivity</b>: Switch between high and low coercivity modes.</li>
            <li><b>Auto-connect</b>: The application will automatically connect to the MSR605 reader on startup.</li>
        </ul>
        
        <p>For more information, please refer to the <a href="https://github.com/Nsfr750/MSR605/wiki">Wiki</a></p>

        """,
        # About text
        "about_title": "About",
        "app_name": "MSR605 Card Reader",
        "version": "Version {version}",
        "github": "GitHub",
        "system_information": "System Information",
        "operating_system": "Operating System",
        "error_loading_system_info": "Error loading system information",
        "about_description": "This application is developed and maintained by a single developer.\nYour support helps keep the project alive and allows for new features and improvements.",
        "copyright": "© 2025 Nsfr750",
        "license": "Licensed under the GPLv3 License",

        # Sponsor dialog
        "support_title": "Support MSR605",
        "support_project": "Support the Project",
        "support_project_header": " Support MSR605",
        "support_project_description": "This application is developed and maintained by a single developer.\nYour support helps keep the project alive and allows for new features and improvements.",
        "support_on_patreon": "Support on Patreon",
        "donate_via_paypal": "Donate via PayPal",
        "copy_address": "Copy Address",
        "address_copied": "Address Copied",
        "address_copied_to_clipboard": "Address Copied to Clipboard",
        "support_development": "Support Development",
        "support_app_name": "Support MSR605",
        "support_message": "If you find this application useful, we invite you to support its development.\n\nYour support helps cover hosting costs and encourages further development.",
        "github_sponsors": "GitHub Sponsors",
        "paypal_donation": "PayPal Donatiopn",
        "monero": "Monero",
        "scan_to_donate_xmr": "Scan to donate XMR",
        "qr_generation_failed": "QR generation failed",
        "ways_to_support": "Ways to Support",
        "other_ways_to_help": "Other Ways to Help",
        "star_on_github": "Star on GitHub",
        "report_bugs": "Report Bugs",
        "share_with_others": "Share with Others",
        "copied": "Copied!",
        "close": "Close",
        "donate_with_paypal": "Donate with PayPal",
        "copy_monero_address": "Copy Monero Address",
                
        # Log viewer
        "save_log_file": "Save Log File",
        "log_files": "Log File (*.log);;All Files (*)",
        "logs_saved": "Logs saved successfully in: {path}",
        "failed_save_logs": "Failed to save log file: {error}",
        "log_level": "Log Level",
        "all_levels": "All Level",
        "refresh": "Refresh",
        "select_log_file": "Select Log file",
        "no_logs_found": "No Logs Found",
        "log_level_filters": "Log Level Filters",
        "clear_log": "Clear Log",
        "save_as": "Save As",
        "no_logs_available": "No Logs Available",
        "log_viewer": "Log Viewer",
        "filter_logs": "Filter Logs",
        "no_log_file": "No Log File",
        "error_reading_log": "Error reading log: {error}",
        "confirm_clear_logs": "Are you sure you want to clear all logs? Thos action cannot be undone.",
        "save_logs": "Save Logs",
        "delete_log": "Delete Log",
        "delete_log_tooltip": "Delete the selected log file",
        "delete_log_confirmation": "Are you sure you want to delete the selected log file? This action cannot be undone.",
        "delete_log_failed": "Failed to delete log file: {error}",
        "delete_log_success": "Log file deleted successfully.",
        "delete_log_failed_title": "Failed to delete log file",
        "delete_log_success_title": "Log file deleted successfully",
        "confirm_delete": "Confirm Delete",
        "confirm_delete_log": "Confirm Delete",
        "confirm_delete_log_title": "Confirm Delete",
        "log_moved_to_trash": "Log file moved to trash: {file}",
        "log_permanently_deleted": "Log file permanently deleted: {file}",
        "log_deleted": "Log file deleted: {file}",
        "error_deleting_log": "Error deleting log file: {error}",
        "yes": "Yes",
        "no": "No",
        
        # Update checker
        "update_available": "Update Available",
        "new_version_available": "New version available!",
        "download_update": "Download Update",
        "remind_me_later": "Remind me later",
        "skip_this_version": "Skip this version",
        "checking_for_updates": "Checking for updates...",
        "up_to_date": "You are up to date.",
        "update_error": "Error checking for updates",
        "update_check_failed": "Failed to check for updates: {error}",
        "release_notes": "Release Notes",
        "download": "Download",
        "view_changes": "View Changes",
        "update_available_title": "Update Available",
        "current_version": "Current Version: {version}",
        "latest_version": "Latest Version: {version}",

        # Missing
        'msg_no_track_data': "No Track Data available",
        'lbl_cardholder': "Cardholder",
        'lbl_last_name': "Last Name",
        'lbl_service_code': "Service Code",
        'lbl_card_number': "Card Number",
        'lbl_expiration': "Expiration",
        'lbl_raw_data': "Raw Data",
        'error_key_and_data_required': "Key and Data required",
        'msg_decrypted_with': "Decrypted with success",
        'msg_decryption_failed': "Decryption failed",
        'msg_decryption_failed_msg': "Decryption failed {error}",
        'msg_decryption_failed_title': "Decryption failed",
        'close': "Close",
    },
    "it": {
        # Application
        "app_title": "Lettore/Encoder MSR605 v{version}",
        
        # Advanced Functions
        "adv_tab_decode": "Decodifica Carta",
        "adv_tab_decrypt": "Decifra Dati",
        "adv_tab_visualization": "Visualizzazione",
        "lbl_select_tracks": "Seleziona Tracce da Decodificare:",
        "chk_track_1": "Traccia 1",
        "chk_track_2": "Traccia 2",
        "chk_track_3": "Traccia 3",
        "btn_decode_tracks": "Decodifica Tracce Selezionate",
        "grp_decoded_data": "Dati Decodificati",
        "grp_encryption_key": "Chiave di Crittografia",
        "lbl_key_hex": "Chiave (esadecimale):",
        "placeholder_enter_key": "Inserisci la chiave di crittografia...",
        "grp_algorithm": "Algoritmo",
        "algo_aes256": "AES-256",
        "algo_aes192": "AES-192",
        "algo_aes128": "AES-128",
        "algo_des": "DES",
        "algo_3des": "3DES",
        "grp_data_decrypt": "Dati da Decifrare",
        "placeholder_enter_data": "Inserisci i dati da decifrare o usa 'Carica Dati Traccia'...",
        "btn_load_track": "Carica Dati Traccia",
        "btn_decrypt": "Decifra",
        "lbl_decryption_results": "Risultati Decifratura:",
        "lbl_loading_track": "Caricamento dati traccia...",
        "lbl_no_track_data": "Nessun dato traccia disponibile",
        "lbl_select_track_prompt": "Seleziona la traccia da caricare:",
        "lbl_processing": "Elaborazione in corso...",
        "lbl_decryption_complete": "Decifratura completata",
        "lbl_decryption_failed": "Decifratura fallita",
        
        # Read Tab
        "btn_read_card": "Leggi Carta",
        "read_card_tooltip": "Leggi i dati da una banda magnetica",
        "btn_advanced_functions": "Funzioni Avanzate",
        "lbl_status_ready": "Pronto per leggere la carta...",
        "no_visualizations_available": "Nessuna visualizzazione disponibile. Leggi una carta per vedere le visualizzazioni.",
        "no_data_available": "Nessun dato disponibile",
        "processing_data": "Elaborazione dati della carta in corso...",
        "viz_character_distribution_title": "Distribuzione Caratteri",
        "viz_bit_pattern_title": "Schema Bit",
        "viz_data_density_title": "Densità Dati",
        "viz_field_analysis_title": "Analisi Campi",
        
        # Menu items
        "menu_file": "&File",
        "menu_database": "&Database",
        "menu_tools": "&Strumenti",
        "menu_help": "&Aiuto",
        "menu_sponsor": "&Sponsor",
        "menu_view": "&Visualizza",
        "menu_voice": "&Voce",
        "menu_language": "&Lingua",
        "menu_enable_voice": "Abilita Controllo &Vocale",
        "menu_voice_help": "Aiuto Comandi &Vocali",
        "menu_view_logs": "Visualizza &Log",
        
        # File menu
        "menu_exit": "&Esci",
        "menu_exit_shortcut": "Ctrl+Q",
        
        # Database menu
        "menu_view_database": "&Visualizza Database",
        "menu_export_csv": "&Esporta in CSV",
        "menu_auto_save": "Salva automaticamente le carte lette",
        "menu_allow_duplicates": "Salva carte duplicate",
        
        # Help menu
        "menu_help_contents": "&Guida",
        "menu_check_updates": "Controlla &aggiornamenti",
        "menu_about": "&Informazioni",
        "menu_support": "&Supporta il Progetto",
        
        # Tabs
        "tab_read": "Leggi Carta",
        "tab_write": "Scrivi Carta",
        "tab_database": "Database",
        "tab_settings": "Impostazioni",
        
        # Read tab
        "btn_read_card": "Leggi Carta",
        "lbl_track_data": "Dati Traccia",
        "lbl_status_ready": "Pronto per leggere la carta...",
        "lbl_reading": "Lettura carta in corso...",
        "lbl_read_success": "Carta letta con successo!",
        "lbl_read_error": "Errore durante la lettura della carta",
        
        # Write tab
        "btn_write_card": "Scrivi Carta",
        "btn_clear_tracks": "Pulisci Tracce",
        "lbl_write_status_ready": "Pronto per scrivere sulla carta...",
        "lbl_writing": "Scrittura sulla carta in corso...",
        "lbl_write_success": "Carta scritta con successo!",
        "lbl_write_error": "Errore durante la scrittura sulla carta",
        "lbl_no_data": "Nessun dato da scrivere",
        
        # Database tab
        "btn_refresh": "Aggiorna",
        "btn_export": "Esporta in CSV",
        "lbl_search": "Cerca:",
        "lbl_search_placeholder": "Cerca nel database...",
        "col_date": "Data",
        "col_track1": "Traccia 1",
        "col_track2": "Traccia 2",
        "col_track3": "Traccia 3",
        "col_notes": "Note",
        "export_success": "Esportati con successo {count} record in:\n{path}",
        "export_failed": "Errore durante l'esportazione del database: {error}",
        
        # Settings tab
        "grp_connection": "Impostazioni Connessione",
        "grp_coercivity": "Coercitività",
        "grp_database": "Impostazioni Database",
        "lbl_port": "Porta:",
        "btn_connect": "Connetti",
        "btn_disconnect": "Disconnetti",
        "lbl_hi_coercivity": "Alta Coercitività (300 Oe)",
        "lbl_lo_coercivity": "Bassa Coercitività (300 Oe)",
        "lbl_auto_save": "Salva automaticamente le carte lette nel database",
        "lbl_allow_duplicates": "Consenti carte duplicate nel database",
        
        # Messages
        "msg_not_connected": "Si prega di connettersi prima al lettore MSR605",
        "msg_connection_success": "Connesso a {port}",
        "msg_connection_error": "Errore durante la connessione a {port}: {error}",
        "msg_disconnected": "Disconnesso",
        "msg_no_ports": "Nessuna porta selezionata o disponibile",
        "msg_coercivity_set": "Impostata coercitività {coercivity}",
        "msg_coercivity_error": "Errore durante l'impostazione della coercitività: {error}",
        "msg_reset_error": "Errore durante il reset del MSR605: {error}",
        "msg_import_error": "Errore durante l'importazione del modulo: {module}",
        "msg_database_error": "Errore del database: {error}",
        "msg_confirm_exit": "Sei sicuro di voler uscire?",
        
        # Dialogs
        "dlg_about_title": "Informazioni su MSR605",
        "dlg_help_title": "Guida",
        "dlg_database_title": "Database Carte",
        "dlg_export_title": "Esporta Database in CSV",
        "dlg_confirm_title": "Conferma",
        "dlg_error_title": "Errore",
        "btn_ok": "OK",
        "btn_cancel": "Annulla",
        "btn_close": "Chiudi",
        
        # Help text
        "help_content": """
        <h2>MSR605 - Guida all'uso</h2>
        
        <h3>Utilizzo di base:</h3>
        <ul>
            <li><b>Leggi Carta</b>: Clicca sul pulsante 'Leggi Carta' e striscia una carta nel lettore.</li>
            <li><b>Scrivi Carta</b>: Inserisci i dati nei campi delle tracce e clicca 'Scrivi Carta'.</li>
            <li><b>Pulisci Tracce</b>: Clicca 'Pulisci Tracce' per cancellare tutti i dati delle tracce.</li>
        </ul>
        
        <h3>Funzionalità del Database:</h3>
        <ul>
            <li><b>Visualizza Database</b>: Visualizza tutte le carte precedentemente lette nel database.</li>
            <li><b>Esporta in CSV</b>: Esporta il database delle carte in un file CSV.</li>
            <li><b>Salvataggio automatico</b>: Attiva/disattiva il salvataggio automatico delle carte lette nel database.</li>
            <li><b>Consenti duplicati</b>: Attiva/disattiva il salvataggio di dati di carte duplicati.</li>
        </ul>
        
        <h3>Avanzate:</h3>
        <ul>
            <li><b>Coercitività</b>: Passa tra le modalità di alta e bassa coercitività.</li>
            <li><b>Connessione automatica</b>: L'applicazione si connetterà automaticamente al lettore MSR605 all'avvio.</li>
        </ul>
        
        <p>Per ulteriori informazioni, consultare la <a href="https://github.com/Nsfr750/MSR605/wiki">Wiki</a></p>
        """,
        
        # About text
        "about_title": "Informazioni",
        "app_name": "MSR605 Card Reader",
        "version": "Versione {version}",
        "github": "GitHub",
        "system_information": "Sistema",
        "operating_system": "Sistema Operativo",
        "error_loading_system_info": "Errore nel caricamento delle informazioni di sistema",
        "about_description": "Questa applicazione è sviluppata e mantenuta da un singolo sviluppatore.\nIl tuo supporto aiuta a mantenere in vita il progetto e permette di aggiungere nuove funzionalità e miglioramenti.",
        "copyright": "© 2025 Nsfr750",
        "license": "Licenza GPLv3",
                
        # Sponsor dialog
        "support_title": "Supporta MSR605",
        "support_project": "Supporta il Progetto",
        "support_project_header": " Supporta MSR605",
        "support_project_description": "Questa applicazione è sviluppata e mantenuta da un singolo sviluppatore.\nIl tuo supporto aiuta a mantenere in vita il progetto e permette di aggiungere nuove funzionalità e miglioramenti.",
        "support_on_patreon": "Supporta su Patreon",
        "donate_via_paypal": "Dona con PayPal",
        "copy_address": "Copia Indirizzo",
        "address_copied": "Indirizzo Copiato",
        "address_copied_to_clipboard": "indirizzo copiato negli appunti",
        "support_development": "Supporta lo Sviluppo",
        "support_app_name": "Supporta MSR605",
        "support_message": "Se trovi utile questa applicazione, ti invitiamo a supportare il suo sviluppo.\n\nIl tuo supporto aiuta a coprire i costi di hosting e incoraggia ulteriori sviluppi.",
        "github_sponsors": "GitHub Sponsors",
        "paypal_donation": "Donazione PayPal",
        "monero": "Monero",
        "scan_to_donate_xmr": "Scansiona per donare XMR",
        "qr_generation_failed": "Generazione codice QR fallita",
        "ways_to_support": "Modi per Supportare",
        "other_ways_to_help": "Altri Modi per Aiutare",
        "star_on_github": "Metti una stella al progetto su",
        "report_bugs": "Segnala bug e suggerisci funzionalità",
        "share_with_others": "Condividi con altri che potrebbero trovarlo utile",
        "copied": "Copiato!",
        "close": "Chiudi",
        "donate_with_paypal": "Dona con PayPal",
        "copy_monero_address": "Copia Indirizzo Monero",
        
        # Log viewer
        "log_viewer": "Visualizzatore Log",
        "filter_logs": "Filtra Log",
        "no_log_file": "Nessun file di log disponibile.",
        "error_reading_log": "Errore durante la lettura del file di log: {error}",
        "clear_logs": "Pulisci Log",
        "confirm_clear_logs": "Sei sicuro di voler cancellare tutti i log? Questa azione non può essere annullata.",
        "save_logs": "Salva Log",
        "save_log_file": "Salva File di Log",
        "log_files": "File di Log (*.log);;Tutti i File (*)",
        "logs_saved": "Log salvati con successo in: {path}",
        "failed_save_logs": "Impossibile salvare il file di log: {error}",
        "log_level": "Livello di Log",
        "all_levels": "Tutti i Livelli",
        "refresh": "Aggiorna",
        "select_log_file": "Seleziona File di Log",
        "no_logs_found": "Nessun Log Trovato",
        "log_level_filters": "Filtri Livello Log",
        "clear_log": "Pulisci Log",
        "save_as": "Salva come",
        "no_logs_available": "Nessun Log Disponibile",
        "delete_log": "Elimina Log",
        "delete_log_tooltip": "Elimina il file di log selezionato",
        "delete_log_confirmation": "Sei sicuro di voler eliminare il file di log selezionato? Questa azione non può essere annullata.",
        "delete_log_failed": "Impossibile eliminare il file di log: {error}",
        "delete_log_success": "File di log eliminato con successo.",
        "delete_log_failed_title": "Impossibile eliminare il file di log",
        "delete_log_success_title": "File di log eliminato con successo",
        "confirm_delete": "Conferma Eliminazione",
        "confirm_delete_log": "Conferma Eliminazione",
        "confirm_delete_log_title": "Conferma Eliminazione",
        "confirm_delete_log_message": "Sei sicuro di voler eliminare il file di log selezionato? Questa azione non può essere annullata.",
        "confirm_delete_log_failed": "Impossibile eliminare il file di log: {error}",
        "confirm_delete_log_success": "File di log eliminato con successo.",
        "confirm_delete_log_success_title": "File di log eliminato con successo",
        "confirm_delete_log_failed_title": "Impossibile eliminare il file di log",
        "log_moved_to_trash": "File di log spostato nel cestino: {file}",
        "log_permanently_deleted": "File di log permanentemente eliminato: {file}",
        "log_deleted": "File di log eliminato: {file}",
        "error_deleting_log": "Impossibile eliminare il file di log: {error}",
        "yes": "Sì",
        "no": "No",
            
        # Update checker
        "update_available": "Aggiornamento Disponibile",
        "new_version_available": "È disponibile una nuova versione di MSR605!",
        "current_version": "La tua versione: {current_version}",
        "latest_version": "Ultima versione: {latest_version}",
        "download_update": "Scarica Aggiornamento",
        "remind_me_later": "Ricordamelo più tardi",
        "skip_this_version": "Salta questa versione",
        "checking_for_updates": "Controllo aggiornamenti in corso...",
        "up_to_date": "Stai utilizzando l'ultima versione di MSR605.",
        "update_error": "Errore durante il controllo degli aggiornamenti",
        "update_check_failed": "Impossibile controllare gli aggiornamenti: {error}",
        "release_notes": "Note di Rilascio",
        "download": "Scarica",
        "view_changes": "Visualizza Modifiche",
        "update_available_title": "Aggiornamento Disponibile",
        
        # Missing
        'msg_no_track_data': "Nessun dato traccia disponibile",
        'lbl_cardholder': "Titolare Carta",
        'lbl_last_name': "Cognome",
        'lbl_service_code': "Codice Servizio",
        'lbl_card_number': "Numero Carta",
        'lbl_expiration': "Scadenza",
        'lbl_raw_data': "Dati Raw",
        'error_key_and_data_required': "Chiave e dati richiesti",
        'msg_decrypted_with': "Decifratura completata con successo",
        'msg_decryption_failed': "Decifratura fallita",
        'msg_decryption_failed_msg': "Decifratura fallita: {error}",
        'msg_decryption_failed_title': "Decifratura fallita",
        'close': "Chiudi",
    },
}


# Backward compatibility function
def t(key: str, lang_code: str = "en", **kwargs) -> str:
    """
    Get a translated string for the given key and language.

    Note: This is kept for backward compatibility. New code should use LanguageManager.

    Args:
        key: The translation key
        lang_code: Language code (default: 'en')
        **kwargs: Format arguments for the translation string

    Returns:
        str: The translated string or the key if not found
    """
    try:
        translation = TRANSLATIONS.get(lang_code, {}).get(
            key, TRANSLATIONS.get("en", {}).get(key, key)
        )
        if isinstance(translation, str) and kwargs:
            return translation.format(**kwargs)
        return translation
    except Exception as e:
        print(f"Translation error for key '{key}': {e}")
        return key
