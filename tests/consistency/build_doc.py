"""Build a VOProv document using most record types, and dump it in every format.

Usage: python build_doc.py OUTDIR
Used to compare serialized outputs before/after refactoring.
"""
import os
import sys
import traceback

from voprov.model import VOProvDocument


def build():
    d = VOProvDocument()
    d.add_namespace('ex', 'http://example.org/')
    # descriptions
    d.activityDescription('ex:ad1', 'Calibrate', version='1.0', description='cal', docurl='http://doc', type='calib')
    d.entityDescription('ex:ed1', 'RawData', description='raw')
    d.entityDescription('ex:ed2', 'CalData')
    d.valueDescription('ex:vd1', 'Offset', 'float', unit='mV', ucd='phot.mag', utype='ex:ut')
    d.datasetDescription('ex:dd1', 'Image', 'fits')
    d.usageDescription('ex:ud1', 'ex:ad1', 'input', description='in', multiplicity=1, entityDescription='ex:ed1')
    d.generationDescription('ex:gd1', 'ex:ad1', 'output', multiplicity=1, entityDescription='ex:ed2')
    d.configFileDescription('ex:cfd1', 'ex:ad1', 'conf', 'text')
    d.parameterDescription('ex:pd1', 'ex:ad1', 'threshold', 'float', unit='sigma')
    # agents
    d.agent('ex:ag1', name='Alice', type='Person', email='a@x.org', affiliation='Obs', phone='123',
            address='Paris', url='http://alice')
    d.agent('ex:ag2', name='Software', type='SoftwareAgent')
    # entities
    d.entity('ex:e1', name='raw1', location='/data/raw1', generatedAtTime='2023-01-01T00:00:00',
             comment='c', entityDescription='ex:ed1')
    d.entity('ex:e2', name='cal1', entityDescription='ex:ed2')
    d.valueEntity('ex:v1', 3.5, name='offset', valueDescription='ex:vd1')
    d.datasetEntity('ex:ds1', name='img', location='/img.fits', datasetDescription='ex:dd1')
    d.configFile('ex:cf1', 'conf', '/conf.txt', configFileDescription='ex:cfd1')
    d.parameter('ex:p1', 'threshold', 5, parameterDescription='ex:pd1')
    d.collection('ex:coll1')
    # activities
    d.activity('ex:a1', name='cal run', startTime='2023-01-01T10:00:00', endTime='2023-01-01T11:00:00',
               comment='run', activityDescription='ex:ad1')
    d.activity('ex:a0', name='prev')
    # relations
    d.usage('ex:a1', 'ex:e1', usageDescription='ex:ud1', role='input', time='2023-01-01T10:01:00', identifier='ex:u1')
    d.generation('ex:e2', 'ex:a1', generationDescription='ex:gd1', role='output', time='2023-01-01T10:59:00',
                 identifier='ex:g1')
    d.start('ex:a1', trigger='ex:e1', starter='ex:a0', time='2023-01-01T10:00:00')
    d.end('ex:a1', trigger='ex:e2', ender='ex:a0', time='2023-01-01T11:00:00')
    d.invalidation('ex:e1', 'ex:a1', time='2023-01-02T00:00:00')
    d.communication('ex:a1', 'ex:a0')
    d.attribution('ex:e2', 'ex:ag1', role='author')
    d.association('ex:a1', 'ex:ag2', role='soft', plan='ex:e1')
    d.delegation('ex:ag2', 'ex:ag1', 'ex:a1')
    d.influence('ex:e2', 'ex:e1')
    d.derivation('ex:e2', 'ex:e1', 'ex:a1')
    d.revision('ex:e2', 'ex:e1')
    d.quotation('ex:e2', 'ex:e1')
    d.primary_source('ex:e2', 'ex:e1')
    d.specialization('ex:e2', 'ex:e1')
    d.alternate('ex:e2', 'ex:e1')
    d.membership('ex:coll1', 'ex:e1')
    d.description('ex:a1', 'ex:ad1')
    d.configuration('ex:a1', 'ex:p1')
    d.configuration('ex:a1', 'ex:cf1', artefactType='ConfigFile')
    d.relate('ex:e1', 'ex:e2')
    d.reference('ex:e1', 'ex:e2')
    # bundle
    b = d.bundle('ex:b1')
    b.entity('ex:be1', name='in bundle')
    b.activity('ex:ba1')
    b.usage('ex:ba1', 'ex:be1')
    return d


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    d = build()
    results = {}

    def attempt(label, fn):
        try:
            out = fn()
            results[label] = 'ok'
            return out
        except Exception as ex:  # noqa
            results[label] = 'FAIL %s: %s' % (type(ex).__name__, str(ex)[:120])
            traceback.print_exc(file=open(os.path.join(outdir, label + '.err'), 'w'))

    for fmt in ['json', 'provn', 'xml', 'yaml', 'rdf']:
        s = attempt('serialize_' + fmt, lambda: d.serialize(format=fmt))
        if s is not None:
            open(os.path.join(outdir, 'doc.' + fmt), 'w').write(s)
            if fmt in ('json', 'xml', 'rdf'):
                def rt():
                    d2 = VOProvDocument.deserialize(content=s, format=fmt)
                    assert d2 == d, 'documents differ'
                attempt('roundtrip_' + fmt, rt)
    w = attempt('get_w3c', lambda: d.get_w3c().serialize(format='json'))
    if w:
        open(os.path.join(outdir, 'w3c.json'), 'w').write(w)
    attempt('unified', lambda: d.unified().serialize(format='json'))
    def dot():
        from voprov.dot import prov_to_dot
        return prov_to_dot(d).to_string()
    s = attempt('dot', dot)
    if s:
        open(os.path.join(outdir, 'doc.dot'), 'w').write(s)
    with open(os.path.join(outdir, 'results.txt'), 'w') as f:
        for k, v in results.items():
            f.write('%s: %s\n' % (k, v))
    print(open(os.path.join(outdir, 'results.txt')).read())


if __name__ == '__main__':
    main(sys.argv[1])
