class Config:
    command = {
        'chrome':'chrome.exe',
        'edge':  'msedge.exe',
        }

    @staticmethod
    def get_browser_config(browser_config):
        browser_config['command'] = '{command} --remote-debugging-port={port} --user-data-dir="{profile_path}"'.format(command = Config.command[browser_config['name']], port = browser_config['port'], profile_path = browser_config['profile_path'])
        return browser_config