from io import BytesIO

import pytest
import pygsti.data as pdata
from pygsti import io
from pygsti.drivers import longsequence as ls
from pygsti.forwardsims import mapforwardsim
from pygsti.modelmembers import operations as operation
from pygsti.models.gaugegroup import UnitaryGaugeGroup
from pygsti.models.modelconstruction import create_explicit_model
from . import fixtures as pkg
from ..util import BaseCase, with_temp_path


# TODO optimize everything
class LongSequenceBasePlain:
    @classmethod
    def setUpClass(cls):
        cls.pspec = pkg.pspec
        cls.model = pkg.model
        cls.maxLens = pkg.maxLengthList
        cls.opLabels = pkg.opLabels
        cls.prep_fids = pkg.prep_fids
        cls.meas_fids = pkg.meas_fids
        cls.germs = pkg.germs
        cls.lsgstStrings = pkg.lsgstStrings
        cls.ds = pkg.dataset

    def setUp(self):
        self.model = self.model.copy()
        self.ds = self.ds.copy()

class LongSequenceBase(LongSequenceBasePlain, BaseCase):
    # just wrap the version that doesn't inherit from BaseCase
    pass


class MapForwardSimulatorWrapper(mapforwardsim.MapForwardSimulator):

    Message = """
        Hit the forward simulator wrapper!
    """

    def _bulk_fill_probs(self, array_to_fill, layout):
        print(self.Message)
        super(MapForwardSimulatorWrapper, self)._bulk_fill_probs(array_to_fill, layout)

    def _bulk_fill_probs_atom(self, array_to_fill, layout_atom, resource_alloc):
        print(self.Message)
        super(MapForwardSimulatorWrapper, self)._bulk_fill_probs_atom(array_to_fill, layout_atom, resource_alloc)



class ModelTestTester(LongSequenceBasePlain):

    def setUp(self):
        super(ModelTestTester, self).setUpClass()
        super(ModelTestTester, self).setUp()
        self.mdl_guess = self.model.depolarize(op_noise=0.01, spam_noise=0.01)

    def test_model_test(self):
        self.setUp()
        result = ls.run_model_test(
            self.mdl_guess, self.ds, self.pspec, self.prep_fids,
            self.meas_fids, self.germs, self.maxLens
        )
        # TODO assert correctness

    def test_model_test_advanced_options(self, capfd: pytest.LogCaptureFixture):
        self.setUp()
        result = ls.run_model_test(
                    self.mdl_guess, self.ds, self.pspec, self.prep_fids,
                    self.meas_fids, self.germs, self.maxLens,
                    advanced_options=dict(objective='chi2', profile=2),
                    simulator=MapForwardSimulatorWrapper
                )
        stdout, _ = capfd.readouterr()
        assert MapForwardSimulatorWrapper.Message in stdout
        # TODO assert correctness

    def test_model_test_pickle_output(self):
        self.setUp()
        with BytesIO() as pickle_stream:
            result = ls.run_model_test(
                self.mdl_guess, self.ds, self.pspec, self.prep_fids,
                self.meas_fids, self.germs, self.maxLens, output_pkl=pickle_stream
            )
            assert len(pickle_stream.getvalue()) > 0
            # TODO assert correctness

    def test_model_test_raises_on_bad_options(self):
        self.setUp()
        with pytest.raises(ValueError):
            ls.run_model_test(
                self.mdl_guess, self.ds, self.pspec, self.prep_fids,
                self.meas_fids, self.germs, self.maxLens,
                advanced_options=dict(objective='foobar')
            )
        with pytest.raises(ValueError):
            ls.run_model_test(
                self.mdl_guess, self.ds, self.pspec, self.prep_fids,
                self.meas_fids, self.germs, self.maxLens,
                advanced_options=dict(profile='foobar')
            )


class StdPracticeGSTTester(LongSequenceBase):
    def setUp(self):
        super(StdPracticeGSTTester, self).setUp()
        self.mdl_guess = self.model.depolarize(op_noise=0.01, spam_noise=0.01)

    def test_stdpractice_gst_TP(self):
        result = ls.run_stdpractice_gst(self.ds, self.model, self.prep_fids, self.meas_fids, self.germs, self.maxLens,
                                        modes="full TP", models_to_test={"Test": self.mdl_guess}, comm=None,
                                        mem_limit=None, verbosity=5)
        # TODO assert correctness

    def test_stdpractice_gst_CPTP(self):
        result = ls.run_stdpractice_gst(self.ds, self.model, self.prep_fids, self.meas_fids, self.germs, self.maxLens,
                                        modes="CPTPLND", models_to_test={"Test": self.mdl_guess}, comm=None,
                                        mem_limit=None, verbosity=5)
        # TODO assert correctness

    def test_stdpractice_gst_Test(self):
        result = ls.run_stdpractice_gst(self.ds, self.model, self.prep_fids, self.meas_fids, self.germs, self.maxLens,
                                        modes="Test", models_to_test={"Test": self.mdl_guess}, comm=None,
                                        mem_limit=None, verbosity=5)
        # TODO assert correctness

    def test_stdpractice_gst_Target(self):
        result = ls.run_stdpractice_gst(self.ds, self.model, self.prep_fids, self.meas_fids, self.germs, self.maxLens,
                                        modes="Target", models_to_test={"Test": self.mdl_guess}, comm=None,
                                        mem_limit=None, verbosity=5)
        # TODO assert correctness
        
    @with_temp_path
    @with_temp_path
    @with_temp_path
    @with_temp_path
    @with_temp_path
    def test_stdpractice_gst_file_args(self, ds_path, model_path, prep_fiducial_path, meas_fiducial_path, germ_path):
        import pickle
        #io.write_model(self.model, model_path)
        io.write_dataset(ds_path, self.ds, self.lsgstStrings[-1])
        io.write_circuit_list(prep_fiducial_path, self.prep_fids)
        io.write_circuit_list(meas_fiducial_path, self.meas_fids)
        io.write_circuit_list(germ_path, self.germs)
        target_model = create_explicit_model(self.pspec, ideal_gate_type='static')
        target_model.write(model_path + '.json')

        result = ls.run_stdpractice_gst(ds_path, model_path+'.json', prep_fiducial_path, meas_fiducial_path, germ_path, self.maxLens,
                                        modes="full TP", comm=None, mem_limit=None, verbosity=5)
        # TODO assert correctness

    def test_stdpractice_gst_gaugeOptTarget(self):
        myGaugeOptSuiteDict = {
            'MyGaugeOpt': {
                'item_weights': {'gates': 1, 'spam': 0.0001}
            }
        }
        target_model = create_explicit_model(self.pspec, ideal_gate_type='static')
        result = ls.run_stdpractice_gst(self.ds, target_model, self.prep_fids, self.meas_fids, self.germs, self.maxLens,
                                        modes="full TP", gaugeopt_suite=myGaugeOptSuiteDict,
                                        gaugeopt_target=self.mdl_guess, comm=None, mem_limit=None, verbosity=5)
        # TODO assert correctness

    def test_stdpractice_gst_gaugeOptTarget_warns_on_target_override(self):
        myGaugeOptSuiteDict = {
            'MyGaugeOpt': {
                'item_weights': {'gates': 1, 'spam': 0.0001},
                'target_model': self.pspec  # to test overriding internal target model (prints a warning)
            }
        }
        with self.assertWarns(Warning):
            target_model = create_explicit_model(self.pspec, ideal_gate_type='static')
            result = ls.run_stdpractice_gst(self.ds, target_model, self.prep_fids, self.meas_fids, self.germs,
                                            self.maxLens, modes="full TP", gaugeopt_suite=myGaugeOptSuiteDict,
                                            gaugeopt_target=self.mdl_guess, comm=None, mem_limit=None, verbosity=5)
            # TODO assert correctness

    def test_stdpractice_gst_advanced_options(self):
        target_model = create_explicit_model(self.pspec, ideal_gate_type='static')
        result = ls.run_stdpractice_gst(self.ds, target_model, self.prep_fids, self.meas_fids, self.germs, self.maxLens,
                                        modes="full TP", comm=None, mem_limit=None, advanced_options={'all': {
                'objective': 'chi2',
                'bad_fit_threshold': -100,  # so we create a robust estimate and convey guage opt to it.
                'on_bad_fit': ["robust"]
            }}, verbosity=5)
        # TODO assert correctness

    def test_stdpractice_gst_pickle_output(self):
        with BytesIO() as pickle_stream:
            target_model = create_explicit_model(self.pspec, ideal_gate_type='static')
            result = ls.run_stdpractice_gst(self.ds, target_model, self.prep_fids, self.meas_fids, self.germs,
                                            self.maxLens, modes="Target", output_pkl=pickle_stream)
            self.assertTrue(len(pickle_stream.getvalue()) > 0)
            # TODO assert correctness

    def test_stdpractice_gst_raises_on_bad_mode(self):
        target_model = create_explicit_model(self.pspec, ideal_gate_type='static')
        with self.assertRaises(ValueError):
            result = ls.run_stdpractice_gst(self.ds, target_model, self.prep_fids, self.meas_fids, self.germs,
                                            self.maxLens, modes="Foobar")


class LongSequenceGSTBase(LongSequenceBase):
    def setUp(self):
        super(LongSequenceGSTBase, self).setUp()
        self.options = {}

    def test_long_sequence_gst(self):
        result = ls.run_long_sequence_gst(
            self.ds, self.model, self.prep_fids, self.meas_fids,
            self.germs, self.maxLens, advanced_options=self.options)
        # TODO assert correctness


class LongSequenceGSTWithChi2(LongSequenceGSTBase):
    def test_long_sequence_gst_chi2(self):
        self.options.update(
            objective='chi2'
        )
        result = ls.run_long_sequence_gst(
            self.ds, self.model, self.prep_fids, self.meas_fids,
            self.germs, self.maxLens,
            advanced_options=self.options)
        # TODO assert correctness


class LongSequenceGSTTester(LongSequenceGSTWithChi2):
    def test_long_sequence_gst_advanced_options(self):
        # TODO what exactly is being tested?
        self.options.update({
            #'starting point': self.model,  #this is deprecated now - need to use protocol objects
            'depolarize_start': 0.05,
            'cptp_penalty_factor': 1.0
        })
        result = ls.run_long_sequence_gst(
            self.ds, self.model, self.prep_fids, None,
            self.germs, self.maxLens,
            advanced_options=self.options
        )
        # TODO assert correctness

    def test_long_sequence_gst_raises_on_bad_profile_options(self):
        #check invalid profile options
        with self.assertRaises(ValueError):
            ls.run_long_sequence_gst(
                self.ds, self.model, self.prep_fids, self.meas_fids,
                self.germs, self.maxLens,
                advanced_options={'profile': 3}
            )

    def test_long_sequence_gst_raises_on_bad_advanced_options(self):
        with self.assertRaises(ValueError):
            ls.run_long_sequence_gst(
                self.ds, self.model, self.prep_fids, None,
                self.germs, self.maxLens,
                advanced_options={'objective': "FooBar"}
            )  # bad objective
        with self.assertRaises(ValueError):
            ls.run_long_sequence_gst(
                self.ds, self.model, self.prep_fids, None,
                self.germs, self.maxLens,
                advanced_options={'starting_point': "FooBar"}
            )  # bad starting point


class WholeGermPowersTester(LongSequenceGSTWithChi2):
    def setUp(self):
        super(WholeGermPowersTester, self).setUp()
        self.options = {} # 'truncScheme': "whole germ powers"}
        # Trunce scheme has been removed as an option - we only ever use whole germ powers now

    @with_temp_path
    @with_temp_path
    @with_temp_path
    @with_temp_path
    @with_temp_path
    def test_long_sequence_gst_with_file_args(self, ds_path, model_path, prep_fiducial_path, meas_fiducial_path, germ_path):
        io.write_dataset(ds_path, self.ds, self.lsgstStrings[-1])
        self.model.write(model_path + '.json')
        io.write_circuit_list(prep_fiducial_path, self.prep_fids)
        io.write_circuit_list(meas_fiducial_path, self.meas_fids)
        io.write_circuit_list(germ_path, self.germs)

        self.options.update(
            randomize_start=1e-6,
            profile=2,
        )
        result = ls.run_long_sequence_gst(
            ds_path, model_path+'.json', prep_fiducial_path, meas_fiducial_path, germ_path, self.maxLens,
            advanced_options=self.options, verbosity=10
        )
        # TODO assert correctness


class CPTPGatesTester(LongSequenceGSTBase):
    # TODO optimize!!
    def setUp(self):
        super(CPTPGatesTester, self).setUp()
        self.model.set_all_parameterizations("CPTPLND")


class SGatesTester(LongSequenceGSTBase):
    def setUp(self):
        super(SGatesTester, self).setUp()
        self.model.set_all_parameterizations("S")


class HPlusSGatesTester(LongSequenceGSTBase):
    # TODO optimize!!!!
    def setUp(self):
        super(HPlusSGatesTester, self).setUp()
        self.model.set_all_parameterizations("H+S")


class GLNDModelTester(LongSequenceGSTBase):
    def setUp(self):
        super(GLNDModelTester, self).setUp()
        for lbl, gate in self.model.operations.items():
            self.model.operations[lbl] = operation.convert(gate, "GLND", "gm")
        self.model.default_gauge_group = UnitaryGaugeGroup(self.model.state_space, "gm")


class MapCalcTester(LongSequenceGSTBase):
    def setUp(self):
        super(MapCalcTester, self).setUp()
        self.model._calcClass = mapforwardsim.MapForwardSimulator
        self.options = {}


class BadFitTester(LongSequenceGSTWithChi2):
    def setUp(self):
        super(BadFitTester, self).setUp()
        self.options = {
            'bad_fit_threshold': -100
        }

class RobustDataScalingTester(LongSequenceGSTBase):
    @classmethod
    def setUpClass(cls):
        super(RobustDataScalingTester, cls).setUpClass()
        datagen_gateset = cls.model.depolarize(op_noise=0.1, spam_noise=0.03).rotate((0.05, 0.13, 0.02))
        ds2 = pdata.simulate_data(
            datagen_gateset, cls.lsgstStrings[-1], num_samples=1000, sample_error='binomial', seed=100
        ).copy_nonstatic()
        ds2.add_counts_from_dataset(cls.ds)
        ds2.done_adding_data()
        cls.ds = ds2

    def setUp(self):
        super(RobustDataScalingTester, self).setUp()
        self.options = {
            'bad_fit_threshold': -100,
            'on_bad_fit': ["do nothing", "robust", "Robust", "robust+", "Robust+"]
        }

    def test_long_sequence_gst_raises_on_bad_badfit_options(self):
        with self.assertRaises(ValueError):
            ls.run_long_sequence_gst(
                self.ds, self.model, self.prep_fids, self.meas_fids,
                self.germs, self.maxLens,
                advanced_options={'bad_fit_threshold': -100,
                                 'on_bad_fit': ["foobar"]}
            )
