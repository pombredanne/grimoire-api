# -*- coding: utf-8 -*-

## Copyright (C) 2014 Bitergia
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
##
## Unit tests for scm_query.py
## 
## Authors:
##   Jesus M. Gonzalez-Barahona <jgb@bitergia.com>
##

from scm_query import buildSession
from datetime import datetime
import unittest

database = 'mysql://jgb:XXX@localhost/vizgrimoire_cvsanaly'
# Set UTF-8, and avoid the DBAPI Unicode support, to use SQLAlchemy's,
# which is said to be more efficient
database += '?charset=utf8&use_unicode=0'

class TestBuildSession (unittest.TestCase):

    def setUp (self):
        self.database = database

    def test_get_session (self):

        session = buildSession(database=self.database, echo=False)

class TestSCMQuery (unittest.TestCase):

    def setUp (self):

        self.database = database
        self.session = buildSession(database=self.database, echo=False)
        self.start = datetime(2014,1,1)
        self.end = datetime(2014,2,1)

    def _test_select_nscmlog (self, variables, results):
        """Test select_nscmlog with different variables

        - variables (list): variables to test
        - results (list): expected results
            Each item in results corresponds to an item in variable
        """

        # Number (count)
        res = self.session.query().select_nscmlog(variables).all()
        self.assertEqual (res, results[0])
        # Number (count), except those that correspond to commits that
        #   doesn't touch files (merges)
        res = self.session.query() \
            .select_nscmlog(variables) \
            .filter_nomerges() \
            .all()
        self.assertEqual (res, results[1])

    def test_select_ncsmlog (self):
        """Test select_ncsmlog"""

        self._test_select_nscmlog (["commits",],
                                   [[(4465L,)], [(4206L,)]])
        self._test_select_nscmlog (["authors",],
                                   [[(14L,)], [(14L,)]])
        self._test_select_nscmlog (["committers",],
                                   [[(14L,)], [(14L,)]])

    def _test_select_nscmlog_period (self, variables, results):
        """Test select_nscmlog with different variables and periods

        - variables (list): variables to test
        - results (list): expected results
            Each item in results corresponds to an item in variables
        """

        # Test for nauthors
        res = self.session.query().select_nscmlog(variables) \
            .filter_period(start=self.start,end=self.end).all()
        self.assertEqual (res, results[0])
        # Test for nauthors that "touch files" (merges are excluded)
        res = self.session.query().select_nscmlog(variables) \
            .filter_nomerges() \
            .filter_period(start=self.start, end=self.end) \
            .all()
        self.assertEqual (res, results[1])
        # Test for nauthors, using authoring date
        res = self.session.query().select_nscmlog(variables) \
            .filter_period(start=self.start, end=self.end, date="author") \
            .all()
        self.assertEqual (res, results[2])

    def test_select_ncsmlog_period (self):
        """Test select_ncsmlog"""

        self._test_select_nscmlog_period (["commits",],
                                          [[(310L,)], [(288,)], [(310,)]])
        self._test_select_nscmlog_period (["authors",],
                                          [[(8L,)], [(7,)], [(8,)]])
        self._test_select_nscmlog_period (["committers",],
                                          [[(8L,)], [(7,)], [(8,)]])

    def test_select_listauthors (self):
        """Test select_listauthors"""

        correct = [(1L, 'Alvaro del Castillo', 'acs@bitergia.com'),
                   (3L, 'Jesus M. Gonzalez-Barahona', 'jgb@gsyc.es'),
                   (4L, 'Daniel Izquierdo', 'dizquierdo@bitergia.com'),
                   (5L, 'Daniel Izquierdo Cortazar', 'dizquierdo@bitergia.com'),
                   (6L, 'Luis Cañas-Díaz', 'lcanas@bitergia.com')]
        res = self.session.query() \
            .select_listauthors() \
            .filter_period(start=self.start, end=self.end) \
            .limit(5).all()
        self.assertEqual (res, correct)

    def _test_select_listpersons (self, kind, correct):
        """Test select_listpersons, for a specific kind of persons

        - kind (string): kind of person: authors, committers, all
        - correct (list): correct results
        """

        res = self.session.query() \
            .select_listpersons(kind) \
            .filter_period(start=self.start, end=self.end) \
            .limit(5).all()
        print res
        self.assertEqual (res, correct)

    def test_select_listpersons (self):
        """Test select_listpersons"""

        correct = {
            "authors":
                [(1L, 'Alvaro del Castillo', 'acs@bitergia.com'),
                 (3L, 'Jesus M. Gonzalez-Barahona', 'jgb@gsyc.es'),
                 (4L, 'Daniel Izquierdo', 'dizquierdo@bitergia.com'),
                 (5L, 'Daniel Izquierdo Cortazar','dizquierdo@bitergia.com'),
                 (6L, 'Luis Cañas-Díaz', 'lcanas@bitergia.com')],
            "committers":
                [(1L, 'Alvaro del Castillo', 'acs@bitergia.com'),
                 (3L, 'Jesus M. Gonzalez-Barahona', 'jgb@gsyc.es'),
                 (4L, 'Daniel Izquierdo', 'dizquierdo@bitergia.com'),
                 (5L, 'Daniel Izquierdo Cortazar', 'dizquierdo@bitergia.com'),
                 (6L, 'Luis Cañas-Díaz', 'lcanas@bitergia.com')],
            "all":
                [(1L, 'Alvaro del Castillo', 'acs@bitergia.com'),
                 (3L, 'Jesus M. Gonzalez-Barahona', 'jgb@gsyc.es'),
                 (4L, 'Daniel Izquierdo', 'dizquierdo@bitergia.com'),
                 (5L, 'Daniel Izquierdo Cortazar', 'dizquierdo@bitergia.com'),
                 (6L, 'Luis Cañas-Díaz', 'lcanas@bitergia.com')]}

        self._test_select_listpersons ("authors", correct["authors"])
        self._test_select_listpersons ("committers", correct["committers"])
        self._test_select_listpersons ("all", correct["all"])

if __name__ == "__main__":
    unittest.main()