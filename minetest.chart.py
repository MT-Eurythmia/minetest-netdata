# -*- coding: utf-8 -*-
import re
from os import access as is_accessible, R_OK
from os.path import isdir, getsize
from base import LogService

ORDER = ['players', 'actions', 'nodes_actions', 'chat_messages']
CHARTS = {
    'players': {
        'options': [None, 'Players', 'players', 'players', 'minetest.players', 'line'],
        'lines': [
            ['players', 'players', 'absolute']
        ]
    },
    'actions': {
        'options': [None, 'Total Actions', 'actions/s', 'actions', 'minetest.actions', 'line'],
        'lines': [
            ['actions', 'actions/s', 'incremental']
        ]
    },
    'nodes_actions': {
        'options': [None, 'Nodes Actions', 'actions/s', 'actions', 'minetest.nodes_actions', 'line'],
        'lines': [
            ['placed_nodes', 'placed nodes/s', 'incremental'],
            ['digged_nodes', 'digged nodes/s', 'incremental']
        ]
    },
    'chat_messages': {
        'options': [None, 'Chat Messages', 'messages/s', 'chat_messages', 'minetest.chat_messages', 'line'],
        'lines': [
            ['chat_messages', 'chat messages/s', 'incremental']
        ]
    },
}

class Service(LogService):
    def __init__(self, configuration=None, name=None):
        LogService.__init__(self, configuration=configuration, name=name)
        self.log_path = self.configuration.get('log_path', '/home/minetest/.minetest/debug.txt')
        self.order = ORDER
        self.definitions = CHARTS
        self.data = {'players': 0, 'actions': 0, 'placed_nodes': 0, 'digged_nodes': 0, 'chat_messages': 0}

    def _get_data(self):
        try:
            raw = self._get_raw_data()
            if not raw:
                return self.data
        except (ValueError, AttributeError):
            return self.data

        for line in raw:
            m = re.match('^\d\d\d\d-\d\d-\d\d [0-2]\d:\d\d:\d\d: ACTION\[Server\]: (.+)', line)
            if m:
                self.data['actions'] += 1
                action = m.group(1)
                if re.match('^\S+ places node \S+ at \([0-9\-]\d*,[0-9\-]\d*,[0-9\-]\d*\)', action):
                    self.data['placed_nodes'] += 1
                elif re.match('^\S+ digs \S+ at \([0-9\-]\d*,[0-9\-]\d*,[0-9\-]\d*\)', action):
                    self.data['digged_nodes'] += 1
                elif re.match('^CHAT: <\S+> .*', action):
                    self.data['chat_messages'] += 1
                elif re.match('^\S+ joins game. List of players: .*', action):
                    self.data['players'] += 1
                elif re.match('^\S+ leaves game. List of players: .*', action):
                    if self.data['players'] > 0:
                        self.data['players'] -= 1
            elif line == '  Separator':
                self.data['players'] = 0

        return self.data

    def check(self):
        """
        :return: bool
        Check if the "log_path" is not empty and readable
        """

        if not (is_accessible(self.log_path, R_OK) and getsize(self.log_path) != 0):
            self.error('%s is not readable or empty' % self.log_path)
            return False
        return True
