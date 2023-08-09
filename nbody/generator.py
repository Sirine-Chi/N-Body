from typing import Optional as opt
from data_manager import YamlManager
from n_body_lib import *

class GeneratingPattern:
    def __init__(self) -> None:
        self.DEFAULT_GENERATING_PATTERN: dict = {
            "number of objects": 2,
            "center": v([0.0, 0.0]),
            "medium radius": 1.0,
            "crit radius delta": 0.25,
            "medium mass": 1.0,
            "mass center velocity": v([0.0, 0.0]),
            "medium velocity scalar": 0.0,
            "velocity crit delta": 0.0
            }
        self.pattern: dict = self.DEFAULT_GENERATING_PATTERN
    
    def set_pattern(self, pattern: dict) -> None:
        """
        Set pattern from dictionary
        """
        self.validate_pattern()
        self.pattern: dict = pattern

    def set_pattern_manually(self, num: int, cen: np.ndarray, med_rad: float, crit_rad_d: float, med_m: float, crit_m_d: float, m_cen_vel: np.ndarray, med_vel_scal: float, vel_crit_d: float) -> None:
        """
        Manually sets parametres to generating pattern dictionary
        """
        self.pattern = {
            "number of objects": num,
            "center": cen,
            "medium radius": med_rad,
            "crit radius delta": crit_rad_d,
            "medium mass": med_m,
            "crit mass delta": crit_m_d,
            "mass center velocity": m_cen_vel,
            "medium velocity scalar": med_vel_scal,
            "velocity crit delta": vel_crit_d
        }

    def load_pattern_from_yaml(self, path_to_yaml):
        """
        Loads pattern from yaml file and sets it
        """
        self.pattern = YamlManager.get_yaml(path_to_yaml)

    def __str__(self) -> str:
        return str(self.pattern)

    def validate_pattern(self):
        for key in self.DEFAULT_GENERATING_PATTERN.items():
            if type(self.DEFAULT_GENERATING_PATTERN[key]) != type(self.pattern[key]):
                line = f"Mistake in option {key},\n your type is {type(self.pattern[key])}, but must be {type(self.DEFAULT_GENERATING_PATTERN[key])}"
                logger.error(line)
        return line

class TableGenerator:
    def __init__(self) -> None:
        pass

    def spherical_sc(self, pattern: opt[dict] = GeneratingPattern().DEFAULT_GENERATING_PATTERN):
        """
        :param pattern: dict | 
        :returns list | 
        """
        objects_data = []
        object_type = "dynamic"
        for i in range(0, pattern["number of objects"]):
            st_der = pattern["crit mass delta"] / 3
            position = pattern["center"] + ranvec(pattern["medium radius"])
            velocity = pattern["center mass velocity"] + ranvec(pattern["medium velocity scalar"])
            objects_data.append(
                [
                    str(object_type),
                    str(i),
                    np.random.normal(pattern["medium mass"], st_der),
                    position[0],
                    position[1],
                    velocity[0],
                    velocity[1],
                    'w',
                    0
                ])
        # print(*objects_data, sep="\n")
        return objects_data


    def write_table(objects_data, path_to_table):
        names = ["Type", "Name", "Mass", "R x", "R y", "V x", "Vy", "Color", "Angle (Deg)"]  # str(type),
        tab = pd.DataFrame(data=objects_data)
        tab.to_csv(path_to_table + 'Generated Table.csv', header=names, index=False)

# Writing generated data to System.TXT
# write_objects(spherical(50, [1, 1], 3, 0, 2, 0.4, [0.2, 0.3], 0.1, 0))

# Writing generated data to System.CSV table
write_table(TableGenerator.spherical_sc(50, [1, 1], 3, 0, 2, 0.4, [0.2, 0.3], 0.1, 0))