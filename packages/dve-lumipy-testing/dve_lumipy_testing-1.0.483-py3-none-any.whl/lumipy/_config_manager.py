from pathlib import Path
import re
from typing import Optional, Union, Dict
from lumipy.common import emph


def is_valid_domain(domain: str) -> bool:
    pattern = re.compile(r'^[a-zA-Z0-9-_]+$')
    if pattern.match(domain):
        return True
    return False


def is_valid_pat(pat: str) -> bool:
    pattern = re.compile(r'^[A-Za-z0-9=_.-]+$')
    if pattern.match(str(pat)):
        return True
    return False


class ConfigManager:
    """Helper class for managing PAT tokens.

    You can add/remove tokens and show them.

      Add:
        config.add('domain', 'token')
      Delete:
        config.delete('domain')
      Show:
        config.show()

    One PAT token is set to active which will be the token and domain used by default in the lumipy
    client/atlas/providers. You can switch between them easily by calling

        config.domain = 'domain-to-switch-to'

    """

    filename = 'auth'
    hidden_dir = '.lumipy'

    title = emph('Lumipy domain config:')

    def __init__(self, _test_dir: Optional[Union[str, Path]] = None):
        """Constructor of the ConfigManager class.

        Args:
            _test_dir (Optional[Union[str, Path]]): set the directory the config manager works in. For testing purposes.

        """
        if _test_dir:
            self.cfg_path = Path(_test_dir) / self.hidden_dir
        else:
            self.cfg_path = Path.home() / self.hidden_dir

        self.cfg_file = self.cfg_path / self.filename

        try:
            self.cfg_path.mkdir(parents=True, exist_ok=True)
            self.cfg_file.touch(exist_ok=True)
        except (PermissionError, OSError) as e:
            err_type = type(e).__name__
            print(
                f"Warning: can't write config file to $HOME/.lumipy (Caught {err_type}). "
                "You will not be able to register and use PATs, so should use another auth method such as env vars or "
                "**kwargs. "
            )

    def __str__(self):
        lines = [self.title] + self._list_lines(False)
        lines.append('Call config.show() to peek at part of the PATs.')
        return '\n'.join(lines)

    def __repr__(self):
        return str(self)

    def show(self, show_pats: Optional[bool] = True):
        """Show the current config content.

        Args:
            show_pats (Optional[bool]): whether to show the PAT strings. Defaults to true.

        """
        lines = self._list_lines(show_pats)
        print(self.title)
        for line in lines:
            print(line)

    def add(self, domain: str, pat: str, overwrite: Optional[bool] = False):
        """Add a PAT token for a domain to the config.

        Args:
            domain (str): the domain to add.
            pat (str): the token to add.
            overwrite (Optional[bool]): whether to overwrite existing entries. Defaults to False so will error.

        """

        if domain is None or not is_valid_domain(domain):
            raise ValueError(f'Invalid domain provided: {domain}')

        if pat is None or not is_valid_pat(pat):
            raise ValueError(f'Invalid PAT')

        domain = domain.lower()
        pats = self._read()
        if not overwrite and domain in pats:
            raise ValueError(f'PAT for {domain} already present. Set overwrite=True to overwrite it.')

        if len(pats) == 0:
            pats[domain] = (pat, True)
        elif domain in pats:
            pats[domain] = (pat, pats[domain][1])
        else:
            pats[domain] = (pat, False)

        self._write(pats)
        self.show(False)

    def delete(self, domain: str):
        """Deletes a domain and its PAT from the config.

        Args:
            domain (str): the domain to remove.

        """
        domain = domain.lower()
        self._check(domain)

        if domain == self.domain:
            raise ValueError(
                f'{domain} is the current active domain. '
                f'Please switch to a different one or call deactivate() before deleting.\n'
                'For example:\n    config.domain = "other"'
            )

        pats = self._read()
        del pats[domain]
        self._write(pats)
        self.show(False)

    def set(self, domain: str):
        """Sets a domain in the config.

        Args:
            domain (str): the domain to set.

        """
        self.domain = domain

    def creds(self, domain: Optional[str] = None) -> Dict[str, str]:
        """Get the credentials (api_url and token) associated with a domain.

        Args:
            domain (Optional[str]): domain to get credentials for. If not specified it will default to the active one.

        Returns:
            Dict[str, str]: dict containing the api_url and token credentials.

        """
        pats = self._read()
        if domain is None and self.domain is None:
            return {}
        elif domain is None:
            domain = self.domain
        else:
            self._check(domain)

        return {'access_token': pats[domain][0], 'api_url': f'https://{domain}.lusid.com/honeycomb'}

    def deactivate(self):
        """Set all domains to inactive.

        """
        pats = self._read()
        self._write({k: (v[0], False) for k, v in pats.items()})
        self.show(False)

    @property
    def domain(self) -> Union[None, str]:
        """Get the currently active domain in the config.

        Returns:
            str: the active domain.

        """
        pats = self._read()
        if len(pats) == 0:
            return None

        lines = [domain for domain, (_, active) in pats.items() if active]

        if len(lines) == 0:
            return None

        if len(lines) == 1:
            return lines[0]

        cmd = 'config.domain = "new-domain"'
        if len(lines) > 1:
            raise ValueError(
                'There are multiple active domain lines in the config. '
                f'Please set a new one with:\n    {cmd}'
            )

    @domain.setter
    def domain(self, new_domain):
        """Switch to a new active domain in the config.

        Args:
            new_domain (str): the new domain to switch to.

        """
        domain = new_domain.lower()
        self._check(domain)
        pats = self._read()

        new = {d: (t, d == domain) for d, (t, _) in pats.items()}
        self._write(new)
        self.show(False)

    def _list_lines(self, show_pats):
        pats = self._read()
        if len(pats) == 0:
            return ['No domain PATs configured. Add one with the config.add() method.']

        lines = []
        max_domain_len = max([len(d) for d in pats.keys()])
        for domain, (token, _) in pats.items():
            lpad = ' '*(max_domain_len - len(domain))
            current = domain == self.domain
            if current:
                domain = emph(f'  {domain}')
            else:
                domain = f'  {domain}'

            front, back = token[:3], token[-5:]
            token = front + '-' * 20 + back
            if not show_pats:
                token = '[PAT hidden]'

            end = emph('(active)') if current else ''
            lines.append(f'{domain}:{lpad} {token} {end}')

        if self.domain is None:
            lines.append('No domain is active. Set one with config.domain = \'domain\'.')

        return lines

    def _check(self, domain):
        domain = domain.lower()
        if domain not in self:
            method = emph(f'config.add("{domain}", <PAT>)')
            raise ValueError(f'Domain {emph(domain)} not found in config. You can add it with {method}.')

    def _read(self):
        if not self.cfg_file.exists():
            return []

        pattern = re.compile(r'\s*:\s*')
        with open(self.cfg_file, 'r') as f:
            lines = f.read().split('\n')
            pats = {}
            for line in lines:
                if re.search(pattern, line):
                    domain, token = re.split(pattern, line)
                    if domain.startswith('#'):
                        pats[domain[1:].strip().lower()] = (token, False)
                    else:
                        pats[domain.strip().lower()] = (token, True)

            return pats

    def _write(self, pats):
        with open(self.cfg_file, 'w') as f:
            content = []
            domains = sorted(pats.keys())
            for domain in domains:
                (token, active) = pats[domain]
                start = '' if active else '#'
                content.append(f'{start}{domain} : {token}')
            f.write('\n'.join(content))

    def __contains__(self, item):
        pats = self._read()
        return item in pats


config = ConfigManager()
