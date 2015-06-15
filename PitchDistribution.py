# -*- coding: utf-8 -*-
import essentia
import essentia.standard as std
import matplotlib.pyplot as pl
import numpy as np
import json

def load(fname):
	with open(fname) as f:    
		dist = json.load(f)
	return PitchDistribution(np.array(dist[0]['bins']), np.array(dist[0]['vals']), kernel_width=dist[0]['kernel_width'], ref_freq=dist[0]['ref_freq'])

class PitchDistribution:
	def __init__(self, pd_bins, pd_vals, kernel_width=7.5, ref_freq=440):
		self.bins = pd_bins
		self.vals = pd_vals
		self.ref_freq = ref_freq
		self.kernel_width = kernel_width
		self.step_size = self.bins[1] - self.bins[0]

	def save(self, fname):
		dist_json = [{'bins':self.bins.tolist(), 'vals':self.vals.tolist(), 'kernel_width':self.kernel_width, 'step_size':self.step_size, 'ref_freq':self.ref_freq}]
		with open(fname, 'w') as f:
			json.dump(dist_json, f, indent = 4)

	def get(self):
		return self.bins, self.vals

	def is_pcd(self):
		"""---------------------------------------------------------------------------------------
		Checks if the pitch distribution is a Pitch Class Distribution
		---------------------------------------------------------------------------------------"""
		return (max(self.bins) == (1200 - self.step_size) and min(self.bins) == 0)

	def detect_peaks(self):
		detector = std.PeakDetection()
		peak_bins, peak_vals = detector(essentia.array(self.vals))
		peak_idxs = [round(bn * len(self.bins)) for bn in peak_bins]
		if(peak_idxs[0] == 0):
			peak_idxs = np.delete(peak_idxs, [len(peak_idxs) - 1])
			peak_vals = np.delete(peak_vals, [len(peak_vals) - 1])
		return peak_idxs, peak_vals

	def shift(self, shift_idx):
		if(shift_idx):
			if self.is_pcd():
				shifted_vals = np.concatenate((self.vals[shift_idx:], self.vals[:shift_idx]))
			else:
				if(shift_idx > 0): ### Shift towards left
					shifted_vals = np.concatenate((self.vals[shift_idx:], np.zeros(shift_idx)))
				else: ### Shift towards right
					shifted_vals = np.concatenate((np.zeros(abs(shift_idx)), self.vals[:shift_idx]))
			return PitchDistribution(self.bins, shifted_vals, self.kernel_width)
		else:
			return self

	def plot(self):
		pl.figure()
		pl.plot(self.bins, self.vals)
		pl.show()
