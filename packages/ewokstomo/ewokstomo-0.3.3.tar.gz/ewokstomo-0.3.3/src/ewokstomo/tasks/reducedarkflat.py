from ewokscore import Task
from tomoscan.esrf.scan.nxtomoscan import NXtomoScan
import numpy


class ReduceDarkFlat(
    Task,
    input_names=["nx_path"],
    optional_input_names=[
        "dark_reduction_method",
        "flat_reduction_method",
        "overwrite",
        "output_dtype",
        "return_info",
    ],
    output_names=[
        "reduced_darks_path",
        "reduced_flats_path",
    ],
):
    def run(self):
        """
        Reduces the dark and flat of the input nx file
        """

        d_reduction_method = self.get_input_value("dark_reduction_method", "mean")
        f_reduction_method = self.get_input_value("flat_reduction_method", "median")
        overwrite = self.get_input_value("overwrite", True)
        output_dtype = self.get_input_value("output_dtype", numpy.float32)
        return_info = self.get_input_value("return_info", False)

        scan = NXtomoScan(self.inputs.nx_path, entry="entry0000")

        reduced_dark = scan.compute_reduced_darks(
            reduced_method=d_reduction_method,
            overwrite=overwrite,
            output_dtype=output_dtype,
            return_info=return_info,
        )
        reduced_flat = scan.compute_reduced_flats(
            reduced_method=f_reduction_method,
            overwrite=overwrite,
            output_dtype=output_dtype,
            return_info=return_info,
        )

        scan.save_reduced_darks(reduced_dark)
        scan.save_reduced_flats(reduced_flat)

        self.outputs.reduced_darks_path = self.inputs.nx_path.replace(
            ".nx", "_darks.hdf5"
        )
        self.outputs.reduced_flats_path = self.inputs.nx_path.replace(
            ".nx", "_flats.hdf5"
        )
