import asyncio

from aiozmq import rpc

from bwapy import BwaAligner

import logging
logger = logging.getLogger(__name__)


class BwapyServe(rpc.AttrHandler):

    def __init__(self, index, *args, map_opts={'x':'ont2d'}, **kwargs):
        """bwa mem alignment server implementation using python binding.

        :param index: bwa index base path, or list thereof.
        :param map_opts: command line options for bwa mem as dictionary.

        """
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger('BwaServe')
        self.index = index

        # expand map_opts to a string:
        opts = []
        for k, v in map_opts.items():
            opts.append('-{} {}'.format(k, v))
        self.bwa_opts = ' '.join(opts)

        self.aligner = None
        self.aligner = BwaAligner(self.index, options=self.bwa_opts)
        self.logger.info('bwa service started.')

    def _clean_index(self):
        self.logger.info('Cleaning alignment proxy.')
        self.aligner = None

    def __del__(self):
            self._clean_index()

    @rpc.method
    def clean_index(self):
        """Destroy the aligner object, which will cleanup the index in memory."""
        self._clean_index()

    @rpc.method
    @asyncio.coroutine
    def align(self, sequence):
        """Align a base sequence.

        :param sequence: sequence to align.

        :returns: the output of bwa mem call.
        """
        if self.aligner is None:
            self.aligner = BwaAligner(self.index, options=self.bwa_opts)
        self.logger.debug("Aligning sequence of length {}.".format(len(sequence)))
        results = self.aligner.align_seq(sequence)
        self.logger.info("Aligned sequence of {} bases with {} hits.".format(
            len(sequence), len(results)
        ))
        return results

