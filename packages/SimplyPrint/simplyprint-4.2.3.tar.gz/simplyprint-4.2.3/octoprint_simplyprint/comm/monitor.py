import psutil
import time


class Monitor:

	def __init__(self, logger):
		self.__logger = logger
		self.__init_process()
		self.__init_children()

	def __get_cpu_temp(self, temp):
		if temp is None:
			return None
		cpu_temp = None
		if "coretemp" in temp:
			cpu_temp = temp["coretemp"][0]._asdict()
		if "cpu-thermal" in temp:
			cpu_temp = temp["cpu-thermal"][0]._asdict()
		if "cpu_thermal" in temp:
			cpu_temp = temp["cpu_thermal"][0]._asdict()
		if "soc_thermal" in temp:
			cpu_temp = temp["soc_thermal"][0]._asdict()
		return cpu_temp

	def __init_process(self):
		self.__process = psutil.Process()
		self.__logger.debug("self.__process is now %r" % (self.__process,))
		# First call so it does not return 0 on next call
		self.__process.cpu_percent()

	def get_cpu(self):
		cpu_freq = psutil.cpu_freq()
		self.__logger.debug("cpu_freq() : %r" % (cpu_freq,))
		cores = psutil.cpu_percent(percpu=True)
		self.__logger.debug("cpu_percent(percpu=True) : %r" % (cores,))
		average = psutil.cpu_percent()
		self.__logger.debug("cpu_percent() : %r" % (average,))
		core_count = psutil.cpu_count(logical=False)
		self.__logger.debug("cpu_count(logical=False) : %r" % (core_count,))
		thread_count = psutil.cpu_count(logical=True)
		self.__logger.debug("cpu_count(logical=True) : %r" % (thread_count,))
		pids = len(psutil.pids())
		self.__logger.debug("len(pids()) : %r" % (pids,))
		boot_time = psutil.boot_time()
		self.__logger.debug("boot_time() : %r" % (boot_time,))
		return dict(
			cores=cores,
			average=average,
			frequency=cpu_freq._asdict() if cpu_freq else dict(),
			core_count=core_count,
			thread_count=thread_count,
			pids=pids,
			uptime=int(time.time() - boot_time),
			octoprint=self.__get_octoprint_cpu(average)
		)

	def __init_children(self):
		try:
			self.__children = self.__process.children(recursive=True)
		except psutil.NoSuchProcess:
			self.__logger.debug("No process found when calling children(recursive=True) on %r" % (self.__process,))
			self.__init_process()
			self.__children = self.__process.children(recursive=True)
		for child in self.__children:
			# First call so it does not return 0 on next call, process might die between calls
			try:
				child.cpu_percent()
			except psutil.NoSuchProcess:
				self.__logger.debug("No process found when calling cpu_percent() on %r" % (child,))
				pass

	def __get_octoprint_cpu(self, average):
		try:
			# Don't know why and how
			# But his can sometimes raise a NoSuchProcessException
			total_cpu = self.__process.cpu_percent()
		except psutil.NoSuchProcess:
			self.__logger.debug("No process found when calling cpu_percent() on %r" % (self.__process,))
			self.__init_process()
			total_cpu = self.__process.cpu_percent()
		for child in self.__children:
			try:
				total_cpu += child.cpu_percent()
			except psutil.NoSuchProcess:
				self.__logger.debug("No process found when calling cpu_percent() on %r" % (child,))
				pass
		self.__init_children()
		cpu_count = psutil.cpu_count()
		self.__logger.debug("cpu_count() : %r" % (cpu_count,))
		return min(total_cpu / cpu_count, average)

	def get_cpu_temp(self):
		# return dict(
		#   current=20 (celsius only)
		# )
		temps_celsius = None
		if hasattr(psutil, "sensors_temperatures"):
			temps_celsius = psutil.sensors_temperatures()
			self.__logger.debug("sensors_temperatures() : %r" % (temps_celsius,))
		temps_c = self.__get_cpu_temp(temps_celsius)
		return temps_c

	def get_memory(self):
		virtual_memory = psutil.virtual_memory()
		self.__logger.debug("virtual_memory() : %r" % (virtual_memory,))
		return virtual_memory._asdict()

	def get_all_resources(self):
		return dict(
			cpu=self.get_cpu(),
			temp=self.get_cpu_temp(),
			memory=self.get_memory(),
		)
