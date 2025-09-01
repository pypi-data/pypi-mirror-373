from enum import Enum, auto
import os


class TowerBase(Enum):
    Onshore = auto()


class ReferenceModel():

    def strip(self):
        self.output.delete()
        self.remove_wind_steps()

    def remove_wind_steps(self):
        for k in self.wind.keys():
            if k.startswith('wind_ramp_abs'):
                self.wind[k].delete()

    def get_pitch_relative(self, blade_nr):
        try:
            r = self.new_htc_structure.orientation.get_subsection_by_name('hub%d' % blade_nr, field='mbdy1')
            assert r.mbdy2[0] == f'blade{blade_nr}'
        except ValueError:
            r = self.new_htc_structure.orientation.get_subsection_by_name('hub%d' % blade_nr, field='body1')
            assert r.body2[0] == f'blade{blade_nr}'

        return r

    def set_fixed_pitch_rotorspeed(self, pitch, rotor_speed, shaft_bearing_name='shaft_rot'):
        self.dll.delete()
        # if 'output' in self:
        #     for s in [s for s in self.output.sensors if s.type == 'constraint']:
        #         s.delete()

        shaft_rot = self.new_htc_structure.constraint.get_subsection_by_name(shaft_bearing_name)
        shaft_rot.name_ = 'bearing3'
        shaft_rot.omegas = rotor_speed

        for i in [1, 2, 3]:
            r = self.get_pitch_relative(i)
            r.body2_eulerang = [0, 0, -pitch]
            c = self.new_htc_structure.constraint.get_subsection_by_name('pitch%d' % i)
            c.name_ = 'fix1'
            c.name.delete()
            c.bearing_vector.delete()

    def make_onshore(self):
        if 'hydro' in self:
            self.hydro.delete()

    def add_standard_output(self):
        output = self.add_section('output', members=dict(
            filename=f'./res/{os.path.basename(self.filename)}',
            data_format='gtsdf',
            buffer=10000))

        for args in [('general', 'time'),
                     ('aero', 'omega'),
                     ('aero', 'azimuth', [1]),
                     ('aero', 'torque'),
                     ('aero', 'thrust'),
                     ('wind', 'free_wind_center_pos0', [1])]:
            output.add_sensor(*args)

    def set_tilt_cone_yaw(self, tilt, cone, yaw=0):
        mbdy = 'mbdy'
        if 'body' in self.new_htc_structure.orientation.base:
            # old names used
            mbdy = 'body'

        self.new_htc_structure.orientation

        r = self.new_htc_structure.orientation.get_subsection_by_name('towertop', f'{mbdy}1')
        r[f'{mbdy}2_eulerang__2'] = [tilt, 0, 0]
        r[f'{mbdy}2_eulerang__2'].comments = "%d deg tilt angle" % tilt
        for i in [1, 2, 3]:
            r = self.new_htc_structure.orientation.get_subsection_by_name('hub%d' % i, f'{mbdy}2')
            r[f'{mbdy}2_eulerang__3'] = [cone, 0, 0]
            r[f'{mbdy}2_eulerang__3'].comments = "%d deg cone angle" % cone
        r = self.new_htc_structure.orientation.get_subsection_by_name('tower', f'{mbdy}1')
        r[f'{mbdy}2_eulerang'] = [0, 0, yaw]
