#  Copyright Ralf Sippl (https://git.io/fjCrU) and other contributors
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
Inspect GStreamer registry in a simple script
(and check out how it all works)
"""

import gi

gi.require_version('Gst', '1.0')
gi.require_version('GLib', '2.0')
from gi.repository import Gst, GObject


def main():
    Gst.init(None)
    reg = Gst.Registry.get()
    plugins = reg.get_plugin_list()
    for plugin in plugins:
        # TODO check if plugin is blacklisted
        plugin_name = plugin.get_name()
        plugin_description = plugin.get_description()
        plugin_filename = plugin.get_filename()
        plugin_version = plugin.get_version()
        plugin_license = plugin.get_license()
        plugin_source = plugin.get_source()
        plugin_date = plugin.get_release_date_string()
        plugin_package = plugin.get_package()
        plugin_origin = plugin.get_origin()

        print("Plugin: ", plugin_name)
        print(" Description:", plugin_description)
        print(" Filename:", plugin_filename)
        print(" Version:", plugin_version)
        print(" License:", plugin_license)
        print(" Source module:", plugin_source)
        print(" Source release date:", plugin_date)
        print(" Binary package:", plugin_package)
        print(" Origin URL:", plugin_origin)

        features = reg.get_feature_list_by_plugin(plugin_name)
        for feature in features:
            feature_rank = feature.get_rank()
            name = feature.get_name()
            if isinstance(feature, Gst.ElementFactory):
                element_factory = feature
                long_name = element_factory.get_metadata(Gst.ELEMENT_METADATA_LONGNAME)
                # TODO rank, metadata
                klass = element_factory.get_metadata(Gst.ELEMENT_METADATA_KLASS)
                description = element_factory.get_metadata(Gst.ELEMENT_METADATA_DESCRIPTION)
                author = element_factory.get_metadata(Gst.ELEMENT_METADATA_AUTHOR)
                print("   {}: {} - {} - rank={}".format(name, long_name, description, feature_rank))
                print("    class:", klass)
                print("    author:", author)

                static_pad_templates = element_factory.get_static_pad_templates()
                print("    pad templates:")
                for static_pad_template in static_pad_templates:
                    name = static_pad_template.name_template
                    direction = static_pad_template.direction.value_nick
                    presence = static_pad_template.presence.value_nick
                    caps = static_pad_template.static_caps.get()
                    print("     {} ({}, {})".format(name, direction, presence))
                    print("      Capabilities:")
                    if caps:
                        if caps.is_any():
                            print("       ANY")
                        elif caps.is_empty():
                            print("       EMPTY")
                        else:
                            caps_count = caps.get_size()
                            for i in range(caps_count):
                                structure = caps.get_structure(i)
                                features = caps.get_features(i)
                                if features:
                                    # TODO exclude Gst.CAPS_FEATURE_MEMORY_SYSTEM_MEMORY?
                                    print("       {} (features: {})".format(structure.to_string(),
                                                                            features.to_string()))
                                else:
                                    print("       {}".format(structure.to_string()))

                print_element_details(element_factory, "    ")  # SLOW

            elif isinstance(feature, Gst.TypeFindFactory):
                type_find_factory = feature
                extensions = type_find_factory.get_extensions()
                print("   {} (typefind) - extensions: {} - rank={}".format(name, extensions, feature_rank))
            elif isinstance(feature, Gst.DeviceProviderFactory):
                device_provider_factory = feature
                long_name = device_provider_factory.get_metadata(Gst.ELEMENT_METADATA_LONGNAME)
                print("   {} (device provider) - {} - rank={}".format(name, long_name, feature_rank))
            elif isinstance(feature, Gst.TracerFactory):
                print("   {} (tracer) - rank={}".format(name, feature_rank))
            elif isinstance(feature, Gst.DynamicTypeFactory):
                print("   {} (dynamictype) - rank={}".format(name, feature_rank))
            else:
                print("   {} ({})".format(name, type(feature).__name__))


def print_element_details(element_factory, indent_prefix):
    element = element_factory.create(None)
    print("{}Element Properties:".format(indent_prefix))
    print_object_properties(element, indent_prefix + " ")
    pass


def print_object_properties(obj, indent_prefix):
    obj_class = type(obj)
    property_specs = obj_class.list_properties()
    for param in property_specs:
        name = param.name
        flags = param.flags
        flags_list = []
        if flags & GObject.ParamFlags.READABLE:
            flags_list.append('readable')
            if flags & GObject.ParamFlags.WRITABLE:
                flags_list.append('writable')
        if flags & GObject.ParamFlags.DEPRECATED:
            flags_list.append('deprecated')
        if flags & Gst.PARAM_CONTROLLABLE:
            flags_list.append('controllable')
        if flags & Gst.PARAM_MUTABLE_PLAYING:
            flags_list.append('mutable-playing')
        if flags & Gst.PARAM_MUTABLE_PAUSED:
            flags_list.append('mutable-paused')
        if flags & Gst.PARAM_MUTABLE_READY:
            flags_list.append('mutable-ready')
        default_value = param.default_value
        value_type = param.value_type
        if value_type.is_a(GObject.GEnum):
            default_value = default_value.value_nick
            # TODO get all enum values
        blurb = param.blurb
        print("{}{} (default: {}): {}".format(indent_prefix, name, default_value, blurb))
        print(" {}Type:{}".format(indent_prefix, value_type.name))
        print(" {}Flags:{}".format(indent_prefix, flags_list))


if __name__ == '__main__':
    main()
