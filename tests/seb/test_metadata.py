from pydavinci.metadata import MetadataGroups

x = MetadataGroups.SHOT_SCENE.fields

for item in x:
    print(item)

print('EOF')