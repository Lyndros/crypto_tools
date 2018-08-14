#!/usr/bin/env python3
# Copyright (c) 2018 Lyndros
# Distributed under the MIT/X11 software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
import pandas as pd
perf = pd.read_pickle('buy_btc_simple_out.pickle') # read in perf DataFrame
print(perf.head())
