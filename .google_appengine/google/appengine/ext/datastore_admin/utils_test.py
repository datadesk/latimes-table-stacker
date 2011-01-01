#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Tests for google.appengine.ext.datastore_admin.utils."""


import datetime

from google.testing.pybase import googletest
from google.appengine.ext.datastore_admin import utils


class UtilsTest(googletest.TestCase):
  """Tests util module functions."""

  def testFormatThousands(self):
    """Tests the FormatThousands() function."""
    self.assertEqual('0', utils.FormatThousands(0))
    self.assertEqual('0.00', utils.FormatThousands(0.0))
    self.assertEqual('0', utils.FormatThousands('0'))
    self.assertEqual('0.0', utils.FormatThousands('0.0'))
    self.assertEqual('7', utils.FormatThousands(7))
    self.assertEqual('65', utils.FormatThousands('65'))
    self.assertEqual('432', utils.FormatThousands(432))
    self.assertEqual('432.00', utils.FormatThousands(432.0))
    self.assertEqual('1,234', utils.FormatThousands(1234))
    self.assertEqual('1,234.56', utils.FormatThousands(1234.56))
    self.assertEqual('1,234.57', utils.FormatThousands(1234.567))
    self.assertEqual('1,234.567', utils.FormatThousands('1234.567'))
    self.assertEqual('1,234.5678', utils.FormatThousands('1234.5678'))

    self.assertEqual('-7', utils.FormatThousands(-7))
    self.assertEqual('-65', utils.FormatThousands('-65'))
    self.assertEqual('-432', utils.FormatThousands(-432))
    self.assertEqual('-432.00', utils.FormatThousands(-432.0))
    self.assertEqual('-1,234', utils.FormatThousands(-1234))
    self.assertEqual('-1,234.56', utils.FormatThousands(-1234.56))
    self.assertEqual('-1,234.57', utils.FormatThousands(-1234.567))
    self.assertEqual('-1,234.567', utils.FormatThousands('-1234.567'))
    self.assertEqual('-1,234.5678', utils.FormatThousands('-1234.5678'))

  def testGetPrettyBytes(self):
    """Test _GetPrettyBytes method."""
    self.assertEqual('1023 Bytes', utils.GetPrettyBytes(1023))
    self.assertEqual('1 KByte', utils.GetPrettyBytes(1024))
    self.assertEqual('1023 KBytes', utils.GetPrettyBytes(1047575))
    self.assertEqual('1 MByte', utils.GetPrettyBytes(1048576))
    self.assertEqual('1023 MBytes', utils.GetPrettyBytes(1072741823))
    self.assertEqual('1 GByte', utils.GetPrettyBytes(1073741824))
    self.assertEqual('1023 GBytes', utils.GetPrettyBytes(1098511627775))
    self.assertEqual('1 TByte', utils.GetPrettyBytes(1099511627776))
    self.assertEqual('1023 TBytes', utils.GetPrettyBytes(1124899906842623))
    self.assertEqual('1 PByte', utils.GetPrettyBytes(1125899906842624))
    self.assertEqual('1023 PBytes', utils.GetPrettyBytes(1151921504606846175))
    self.assertEqual('1 EByte', utils.GetPrettyBytes(1152921504606846976))

    self.assertEqual('1023 Bytes', utils.GetPrettyBytes(1023, 1))
    self.assertEqual('984.9 KBytes', utils.GetPrettyBytes(1008574, 1))
    self.assertEqual('966.8 MBytes', utils.GetPrettyBytes(1013741823, 1))
    self.assertEqual('940.181 GBytes', utils.GetPrettyBytes(1009511627775, 3))
    self.assertEqual('914.86 TBytes', utils.GetPrettyBytes(1005899906842623, 2))
    self.assertEqual('1.320 PBytes', utils.GetPrettyBytes(1485899906842624, 3))
    self.assertEqual('1.538 EBytes',
                     utils.GetPrettyBytes(1772921504606846976, 3))


if __name__ == '__main__':
  googletest.main()
