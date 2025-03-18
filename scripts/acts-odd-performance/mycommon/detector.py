import acts
from acts.examples.odd import getOpenDataDetector, getOpenDataDetectorDirectory


u = acts.UnitConstants


_odd_cache = None


def get_odd():
    global _odd_cache
    if _odd_cache is not None:
        return _odd_cache

    # ODD configs
    geo_dir = getOpenDataDetectorDirectory()
    material_map = geo_dir / "data/odd-material-maps.root"
    digi_config = geo_dir / "config/odd-digi-smearing-config.json"
    seeding_sel = geo_dir / "config/odd-seeding-config.json"
    material_deco = acts.IMaterialDecorator.fromFile(material_map)

    # ODD
    detector = getOpenDataDetector(odd_dir=geo_dir, mdecorator=material_deco)
    tracking_geometry = detector.trackingGeometry()
    decorators = detector.contextDecorators()
    field = acts.ConstantBField(acts.Vector3(0.0, 0.0, 2.0 * u.T))

    _odd_cache = (
        detector,
        tracking_geometry,
        decorators,
        field,
        digi_config,
        seeding_sel,
    )
    return _odd_cache
