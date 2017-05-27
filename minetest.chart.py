# -*- coding: utf-8 -*-
import re
from os import access as is_accessible, R_OK
from os.path import isdir, getsize
from base import LogService

ORDER = ['players', 'actions', 'nodes_actions', 'chat_messages', 'errors']
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
    'errors': {
        'options': [None, 'Errors and Warnings', 'error/s', 'errors_and_warnings', 'minetest.errors', 'line'],
        'lines': [
            ['errors', 'errors/s', 'incremental'],
            ['warnings', 'warnings/s', 'incremental']
        ]
    }
}

event_regexp = re.compile('^\d\d\d\d-\d\d-\d\d [0-2]\d:\d\d:\d\d: (\w+)\[Server\]: (.+)')
node_placed_regexp = re.compile('^\S+ places node \S+ at \([0-9\-]\d*,[0-9\-]\d*,[0-9\-]\d*\)')
node_digged_regexp = re.compile('^\S+ digs \S+ at \([0-9\-]\d*,[0-9\-]\d*,[0-9\-]\d*\)')
chat_regexp = re.compile('^CHAT: <\S+> .*')
player_join_regexp = re.compile('^\S+ joins game. List of players: .*')
player_leave_regexp = re.compile('^\S+ leaves game. List of players: .*')
player_times_out_regexp = re.compile('^\S+ times out. List of players: .*')

class Service(LogService):
    def __init__(self, configuration=None, name=None):
        LogService.__init__(self, configuration=configuration, name=name)
        self.log_path = self.configuration.get('log_path', '/home/minetest/.minetest/debug.txt')
        self.order = ORDER
        self.definitions = CHARTS
        self.data = {'players': 0, 'actions': 0, 'warnings': 0, 'errors': 0, 'placed_nodes': 0, 'digged_nodes': 0, 'chat_messages': 0}

    def _get_data(self):
        try:
            raw = self._get_raw_data()
            if not raw:
                return self.data
        except (ValueError, AttributeError):
            return self.data

        for line in raw:
            m = event_regexp.match(line)
            if m:
                event_type = m.group(1)
                if event_type == 'ACTION':
                    self.data['actions'] += 1
                    action = m.group(2)
                    if node_placed_regexp.match(action):
                        self.data['placed_nodes'] += 1
                    elif node_digged_regexp.match(action):
                        self.data['digged_nodes'] += 1
                    elif chat_regexp.match(action):
                        self.data['chat_messages'] += 1
                    elif player_join_regexp.match(action):
                        self.data['players'] += 1
                    elif player_leave_regexp.match(action) or player_times_out_regexp.match(action):
                        if self.data['players'] > 0:
                            self.data['players'] -= 1
                elif event_type == 'ERROR':
                    self.data['errors'] += 1
                elif event_type == 'WARNING':
                    self.data['warnings'] += 1
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
