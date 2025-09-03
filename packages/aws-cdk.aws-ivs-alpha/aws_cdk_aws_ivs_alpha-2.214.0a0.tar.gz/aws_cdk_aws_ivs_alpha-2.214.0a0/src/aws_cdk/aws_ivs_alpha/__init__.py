r'''
# AWS::IVS Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

Amazon Interactive Video Service (Amazon IVS) is a managed live streaming
solution that is quick and easy to set up, and ideal for creating interactive
video experiences. Send your live streams to Amazon IVS using streaming software
and the service does everything you need to make low-latency live video
available to any viewer around the world, letting you focus on building
interactive experiences alongside the live video. You can easily customize and
enhance the audience experience through the Amazon IVS player SDK and timed
metadata APIs, allowing you to build a more valuable relationship with your
viewers on your own websites and applications.

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) project.

## Channels

An Amazon IVS channel stores configuration information related to your live
stream. You first create a channel and then contribute video to it using the
channel’s stream key to start your live stream.

You can create a channel

```python
my_channel = ivs.Channel(self, "Channel")
```

You can use Advanced Channel type by setting the `type` property to
`ivs.ChannelType.ADVANCED_HD` or `ivs.ChannelType.ADVANCED_SD`.

Additionally, when using the Advanced Channel type, you can set
the `preset` property to `ivs.Preset.CONSTRAINED_BANDWIDTH_DELIVERY`
or `ivs.Preset.HIGHER_BANDWIDTH_DELIVERY`.

For more information, see [Amazon IVS Streaming Configuration](https://docs.aws.amazon.com/ivs/latest/LowLatencyUserGuide/streaming-config.html).

```python
my_channel = ivs.Channel(self, "myChannel",
    type=ivs.ChannelType.ADVANCED_HD,
    preset=ivs.Preset.CONSTRAINED_BANDWIDTH_DELIVERY
)
```

If you want to use RTMP ingest, set `insecureIngest` property to `true`.
By default, `insecureIngest` is `false` which means using RTMPS ingest.

**⚠ Note:** RTMP ingest might result in reduced security for your streams. AWS recommends that you use RTMPS for ingest, unless you have specific and verified use cases. For more information, see [Encoder Settings](https://docs.aws.amazon.com/ivs/latest/LowLatencyUserGuide/streaming-config.html#streaming-config-settings).

```python
my_rtmp_channel = ivs.Channel(self, "myRtmpChannel",
    type=ivs.ChannelType.STANDARD,
    insecure_ingest=True
)
```

### Multitrack Video

Multitrack video is a new, low-latency streaming paradigm supported by Amazon Interactive Video Service (IVS) and services that use Amazon IVS.

You can use Multitrack Video by setting the `multitrackInputConfiguration` property.
Multitrack Video requires both a STANDARD Channel and Fragmented Mp4.

For more information, see [Amazon IVS Multitrack Video](https://docs.aws.amazon.com/ivs/latest/LowLatencyUserGuide/multitrack-video.html).

```python
ivs.Channel(self, "ChannelWithMultitrackVideo",
    type=ivs.ChannelType.STANDARD,
    container_format=ivs.ContainerFormat.FRAGMENTED_MP4,
    multitrack_input_configuration=ivs.MultitrackInputConfiguration(
        maximum_resolution=ivs.MaximumResolution.HD,
        policy=ivs.Policy.ALLOW
    )
)
```

### Importing an existing channel

You can reference an existing channel, for example, if you need to create a
stream key for an existing channel

```python
my_channel = ivs.Channel.from_channel_arn(self, "Channel", my_channel_arn)
```

## Stream Keys

A Stream Key is used by a broadcast encoder to initiate a stream and identify
to Amazon IVS which customer and channel the stream is for. If you are
storing this value, it should be treated as if it were a password.

You can create a stream key for a given channel

```python
my_stream_key = my_channel.add_stream_key("StreamKey")
```

## Private Channels

Amazon IVS offers the ability to create private channels, allowing
you to restrict your streams by channel or viewer. You control access
to video playback by enabling playback authorization on channels and
generating signed JSON Web Tokens (JWTs) for authorized playback requests.

A playback token is a JWT that you sign (with a playback authorization key)
and include with every playback request for a channel that has playback
authorization enabled.

In order for Amazon IVS to validate the token, you need to upload
the public key that corresponds to the private key you use to sign the token.

```python
key_pair = ivs.PlaybackKeyPair(self, "PlaybackKeyPair",
    public_key_material=my_public_key_pem_string
)
```

Then, when creating a channel, specify the authorized property

```python
my_channel = ivs.Channel(self, "Channel",
    authorized=True
)
```

## Recording Configurations

An Amazon IVS Recording Configuration stores settings that specify how a channel's live streams should be recorded.
You can configure video quality, thumbnail generation, and where recordings are stored in Amazon S3.

For more information about IVS recording, see [IVS Auto-Record to Amazon S3 | Low-Latency Streaming](https://docs.aws.amazon.com/ivs/latest/LowLatencyUserGuide/record-to-s3.html).

You can create a recording configuration:

```python
# create an S3 bucket for storing recordings
recording_bucket = s3.Bucket(self, "RecordingBucket")

# create a basic recording configuration
recording_configuration = ivs.RecordingConfiguration(self, "RecordingConfiguration",
    bucket=recording_bucket
)
```

### Renditions of a Recording

When you stream content to an Amazon IVS channel, auto-record-to-s3 uses the source video to generate multiple renditions.

For more information, see [Discovering the Renditions of a Recording](https://docs.aws.amazon.com/ivs/latest/LowLatencyUserGuide/record-to-s3.html#r2s3-recording-renditions).

```python
# recording_bucket: s3.Bucket


recording_configuration = ivs.RecordingConfiguration(self, "RecordingConfiguration",
    bucket=recording_bucket,

    # set rendition configuration
    rendition_configuration=ivs.RenditionConfiguration.custom([ivs.Resolution.HD, ivs.Resolution.SD])
)
```

### Thumbnail Generation

You can enable or disable the recording of thumbnails for a live session and modify the interval at which thumbnails are generated for the live session.

Thumbnail intervals may range from 1 second to 60 seconds; by default, thumbnail recording is enabled, at an interval of 60 seconds.

For more information, see [Thumbnails](https://docs.aws.amazon.com/ivs/latest/LowLatencyUserGuide/record-to-s3.html#r2s3-thumbnails).

```python
# recording_bucket: s3.Bucket


recording_configuration = ivs.RecordingConfiguration(self, "RecordingConfiguration",
    bucket=recording_bucket,

    # set thumbnail settings
    thumbnail_configuration=ivs.ThumbnailConfiguration.interval(ivs.Resolution.HD, [ivs.Storage.LATEST, ivs.Storage.SEQUENTIAL], Duration.seconds(30))
)
```

### Merge Fragmented Streams

The `recordingReconnectWindow` property allows you to specify a window of time (in seconds) during which, if your stream is interrupted and a new stream is started, Amazon IVS tries to record to the same S3 prefix as the previous stream.

In other words, if a broadcast disconnects and then reconnects within the specified interval, the multiple streams are considered a single broadcast and merged together.

For more information, see [Merge Fragmented Streams](https://docs.aws.amazon.com/ivs/latest/LowLatencyUserGuide/record-to-s3.html#r2s3-merge-fragmented-streams).

```python
# recording_bucket: s3.Bucket


recording_configuration = ivs.RecordingConfiguration(self, "RecordingConfiguration",
    bucket=recording_bucket,

    # set recording reconnect window
    recording_reconnect_window=Duration.seconds(60)
)
```

### Attaching Recording Configuration to a Channel

To enable recording for a channel, specify the recording configuration when creating the channel:

```python
# recording_configuration: ivs.RecordingConfiguration


channel = ivs.Channel(self, "Channel",
    # set recording configuration
    recording_configuration=recording_configuration
)
```
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@aws-cdk/aws-ivs-alpha.ChannelProps",
    jsii_struct_bases=[],
    name_mapping={
        "authorized": "authorized",
        "channel_name": "channelName",
        "container_format": "containerFormat",
        "insecure_ingest": "insecureIngest",
        "latency_mode": "latencyMode",
        "multitrack_input_configuration": "multitrackInputConfiguration",
        "preset": "preset",
        "recording_configuration": "recordingConfiguration",
        "type": "type",
    },
)
class ChannelProps:
    def __init__(
        self,
        *,
        authorized: typing.Optional[builtins.bool] = None,
        channel_name: typing.Optional[builtins.str] = None,
        container_format: typing.Optional["ContainerFormat"] = None,
        insecure_ingest: typing.Optional[builtins.bool] = None,
        latency_mode: typing.Optional["LatencyMode"] = None,
        multitrack_input_configuration: typing.Optional[typing.Union["MultitrackInputConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
        preset: typing.Optional["Preset"] = None,
        recording_configuration: typing.Optional["IRecordingConfiguration"] = None,
        type: typing.Optional["ChannelType"] = None,
    ) -> None:
        '''(experimental) Properties for creating a new Channel.

        :param authorized: (experimental) Whether the channel is authorized. If you wish to make an authorized channel, you will need to ensure that a PlaybackKeyPair has been uploaded to your account as this is used to validate the signed JWT that is required for authorization Default: false
        :param channel_name: (experimental) A name for the channel. Default: Automatically generated name
        :param container_format: (experimental) Indicates which content-packaging format is used (MPEG-TS or fMP4). If ``multitrackInputConfiguration`` is specified, only fMP4 can be used. Otherwise, ``containerFormat`` may be set to ``ContainerFormat.TS`` or ``ContainerFormat.FRAGMENTED_MP4``. Default: - ``ContainerFormat.FRAGMENTED_MP4`` is automatically set when the ``multitrackInputConfiguration`` is specified. If not specified, it remains undefined and uses the IVS default setting (TS).
        :param insecure_ingest: (experimental) Whether the channel allows insecure RTMP ingest. Default: false
        :param latency_mode: (experimental) Channel latency mode. Default: LatencyMode.LOW
        :param multitrack_input_configuration: (experimental) Object specifying multitrack input configuration. You must specify ``multitrackInputConfiguration`` if you want to use MultiTrack Video. ``multitrackInputConfiguration`` is only supported for ``ChannelType.STANDARD``. Default: undefined - IVS default setting is not use MultiTrack Video.
        :param preset: (experimental) An optional transcode preset for the channel. Can be used for ADVANCED_HD and ADVANCED_SD channel types. When LOW or STANDARD is used, the preset will be overridden and set to none regardless of the value provided. Default: - Preset.HIGHER_BANDWIDTH_DELIVERY if channelType is ADVANCED_SD or ADVANCED_HD, none otherwise
        :param recording_configuration: (experimental) A recording configuration for the channel. Default: - recording is disabled
        :param type: (experimental) The channel type, which determines the allowable resolution and bitrate. If you exceed the allowable resolution or bitrate, the stream will disconnect immediately Default: ChannelType.STANDARD

        :stability: experimental
        :exampleMetadata: infused

        Example::

            my_channel = ivs.Channel(self, "myChannel",
                type=ivs.ChannelType.ADVANCED_HD,
                preset=ivs.Preset.CONSTRAINED_BANDWIDTH_DELIVERY
            )
        '''
        if isinstance(multitrack_input_configuration, dict):
            multitrack_input_configuration = MultitrackInputConfiguration(**multitrack_input_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ebf6a0e98bbd5b88d9676fbe616666a44f837cba80675eade5df1fea22c9d22)
            check_type(argname="argument authorized", value=authorized, expected_type=type_hints["authorized"])
            check_type(argname="argument channel_name", value=channel_name, expected_type=type_hints["channel_name"])
            check_type(argname="argument container_format", value=container_format, expected_type=type_hints["container_format"])
            check_type(argname="argument insecure_ingest", value=insecure_ingest, expected_type=type_hints["insecure_ingest"])
            check_type(argname="argument latency_mode", value=latency_mode, expected_type=type_hints["latency_mode"])
            check_type(argname="argument multitrack_input_configuration", value=multitrack_input_configuration, expected_type=type_hints["multitrack_input_configuration"])
            check_type(argname="argument preset", value=preset, expected_type=type_hints["preset"])
            check_type(argname="argument recording_configuration", value=recording_configuration, expected_type=type_hints["recording_configuration"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if authorized is not None:
            self._values["authorized"] = authorized
        if channel_name is not None:
            self._values["channel_name"] = channel_name
        if container_format is not None:
            self._values["container_format"] = container_format
        if insecure_ingest is not None:
            self._values["insecure_ingest"] = insecure_ingest
        if latency_mode is not None:
            self._values["latency_mode"] = latency_mode
        if multitrack_input_configuration is not None:
            self._values["multitrack_input_configuration"] = multitrack_input_configuration
        if preset is not None:
            self._values["preset"] = preset
        if recording_configuration is not None:
            self._values["recording_configuration"] = recording_configuration
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def authorized(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether the channel is authorized.

        If you wish to make an authorized channel, you will need to ensure that
        a PlaybackKeyPair has been uploaded to your account as this is used to
        validate the signed JWT that is required for authorization

        :default: false

        :stability: experimental
        '''
        result = self._values.get("authorized")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def channel_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) A name for the channel.

        :default: Automatically generated name

        :stability: experimental
        '''
        result = self._values.get("channel_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def container_format(self) -> typing.Optional["ContainerFormat"]:
        '''(experimental) Indicates which content-packaging format is used (MPEG-TS or fMP4).

        If ``multitrackInputConfiguration`` is specified, only fMP4 can be used.
        Otherwise, ``containerFormat`` may be set to ``ContainerFormat.TS`` or ``ContainerFormat.FRAGMENTED_MP4``.

        :default: - ``ContainerFormat.FRAGMENTED_MP4`` is automatically set when the ``multitrackInputConfiguration`` is specified. If not specified, it remains undefined and uses the IVS default setting (TS).

        :stability: experimental
        '''
        result = self._values.get("container_format")
        return typing.cast(typing.Optional["ContainerFormat"], result)

    @builtins.property
    def insecure_ingest(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether the channel allows insecure RTMP ingest.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("insecure_ingest")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def latency_mode(self) -> typing.Optional["LatencyMode"]:
        '''(experimental) Channel latency mode.

        :default: LatencyMode.LOW

        :stability: experimental
        '''
        result = self._values.get("latency_mode")
        return typing.cast(typing.Optional["LatencyMode"], result)

    @builtins.property
    def multitrack_input_configuration(
        self,
    ) -> typing.Optional["MultitrackInputConfiguration"]:
        '''(experimental) Object specifying multitrack input configuration. You must specify ``multitrackInputConfiguration`` if you want to use MultiTrack Video.

        ``multitrackInputConfiguration`` is only supported for ``ChannelType.STANDARD``.

        :default: undefined - IVS default setting is not use MultiTrack Video.

        :see: https://docs.aws.amazon.com/ivs/latest/LowLatencyUserGuide/multitrack-video.html
        :stability: experimental
        '''
        result = self._values.get("multitrack_input_configuration")
        return typing.cast(typing.Optional["MultitrackInputConfiguration"], result)

    @builtins.property
    def preset(self) -> typing.Optional["Preset"]:
        '''(experimental) An optional transcode preset for the channel.

        Can be used for ADVANCED_HD and ADVANCED_SD channel types.
        When LOW or STANDARD is used, the preset will be overridden and set to none regardless of the value provided.

        :default: - Preset.HIGHER_BANDWIDTH_DELIVERY if channelType is ADVANCED_SD or ADVANCED_HD, none otherwise

        :stability: experimental
        '''
        result = self._values.get("preset")
        return typing.cast(typing.Optional["Preset"], result)

    @builtins.property
    def recording_configuration(self) -> typing.Optional["IRecordingConfiguration"]:
        '''(experimental) A recording configuration for the channel.

        :default: - recording is disabled

        :stability: experimental
        '''
        result = self._values.get("recording_configuration")
        return typing.cast(typing.Optional["IRecordingConfiguration"], result)

    @builtins.property
    def type(self) -> typing.Optional["ChannelType"]:
        '''(experimental) The channel type, which determines the allowable resolution and bitrate.

        If you exceed the allowable resolution or bitrate, the stream will disconnect immediately

        :default: ChannelType.STANDARD

        :stability: experimental
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional["ChannelType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ChannelProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-ivs-alpha.ChannelType")
class ChannelType(enum.Enum):
    '''(experimental) The channel type, which determines the allowable resolution and bitrate.

    If you exceed the allowable resolution or bitrate, the stream probably will disconnect immediately.

    :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html
    :stability: experimental
    :exampleMetadata: infused

    Example::

        my_channel = ivs.Channel(self, "myChannel",
            type=ivs.ChannelType.ADVANCED_HD,
            preset=ivs.Preset.CONSTRAINED_BANDWIDTH_DELIVERY
        )
    '''

    STANDARD = "STANDARD"
    '''(experimental) Multiple qualities are generated from the original input, to automatically give viewers the best experience for their devices and network conditions.

    Transcoding allows higher playback quality across a range of download speeds. Resolution can be up to 1080p and bitrate can be up to 8.5 Mbps.
    Audio is transcoded only for renditions 360p and below; above that, audio is passed through.

    :stability: experimental
    '''
    BASIC = "BASIC"
    '''(experimental) Delivers the original input to viewers.

    The viewer’s video-quality choice is limited to the original input.

    :stability: experimental
    '''
    ADVANCED_SD = "ADVANCED_SD"
    '''(experimental) Multiple qualities are generated from the original input, to automatically give viewers the best experience for their devices and network conditions.

    Input resolution can be up to 1080p and bitrate can be up to 8.5 Mbps; output is capped at SD quality (480p).
    Audio for all renditions is transcoded, and an audio-only rendition is available.

    :stability: experimental
    '''
    ADVANCED_HD = "ADVANCED_HD"
    '''(experimental) Multiple qualities are generated from the original input, to automatically give viewers the best experience for their devices and network conditions.

    Input resolution can be up to 1080p and bitrate can be up to 8.5 Mbps; output is capped at HD quality (720p).
    Audio for all renditions is transcoded, and an audio-only rendition is available.

    :stability: experimental
    '''


@jsii.enum(jsii_type="@aws-cdk/aws-ivs-alpha.ContainerFormat")
class ContainerFormat(enum.Enum):
    '''(experimental) Container Format.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        ivs.Channel(self, "ChannelWithMultitrackVideo",
            type=ivs.ChannelType.STANDARD,
            container_format=ivs.ContainerFormat.FRAGMENTED_MP4,
            multitrack_input_configuration=ivs.MultitrackInputConfiguration(
                maximum_resolution=ivs.MaximumResolution.HD,
                policy=ivs.Policy.ALLOW
            )
        )
    '''

    TS = "TS"
    '''(experimental) Use MPEG-TS.

    :stability: experimental
    '''
    FRAGMENTED_MP4 = "FRAGMENTED_MP4"
    '''(experimental) Use fMP4.

    :stability: experimental
    '''


@jsii.interface(jsii_type="@aws-cdk/aws-ivs-alpha.IChannel")
class IChannel(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''(experimental) Represents an IVS Channel.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="channelArn")
    def channel_arn(self) -> builtins.str:
        '''(experimental) The channel ARN.

        For example: arn:aws:ivs:us-west-2:123456789012:channel/abcdABCDefgh

        :stability: experimental
        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="addStreamKey")
    def add_stream_key(self, id: builtins.str) -> "StreamKey":
        '''(experimental) Adds a stream key for this IVS Channel.

        :param id: construct ID.

        :stability: experimental
        '''
        ...


class _IChannelProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''(experimental) Represents an IVS Channel.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-ivs-alpha.IChannel"

    @builtins.property
    @jsii.member(jsii_name="channelArn")
    def channel_arn(self) -> builtins.str:
        '''(experimental) The channel ARN.

        For example: arn:aws:ivs:us-west-2:123456789012:channel/abcdABCDefgh

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "channelArn"))

    @jsii.member(jsii_name="addStreamKey")
    def add_stream_key(self, id: builtins.str) -> "StreamKey":
        '''(experimental) Adds a stream key for this IVS Channel.

        :param id: construct ID.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__809e7d60e77d2ede718027f4d99dcf810db3b33f39daebb557b424c6457e2f22)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast("StreamKey", jsii.invoke(self, "addStreamKey", [id]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IChannel).__jsii_proxy_class__ = lambda : _IChannelProxy


@jsii.interface(jsii_type="@aws-cdk/aws-ivs-alpha.IPlaybackKeyPair")
class IPlaybackKeyPair(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''(experimental) Represents an IVS Playback Key Pair.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="playbackKeyPairArn")
    def playback_key_pair_arn(self) -> builtins.str:
        '''(experimental) Key-pair ARN.

        For example: arn:aws:ivs:us-west-2:693991300569:playback-key/f99cde61-c2b0-4df3-8941-ca7d38acca1a

        :stability: experimental
        :attribute: true
        '''
        ...


class _IPlaybackKeyPairProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''(experimental) Represents an IVS Playback Key Pair.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-ivs-alpha.IPlaybackKeyPair"

    @builtins.property
    @jsii.member(jsii_name="playbackKeyPairArn")
    def playback_key_pair_arn(self) -> builtins.str:
        '''(experimental) Key-pair ARN.

        For example: arn:aws:ivs:us-west-2:693991300569:playback-key/f99cde61-c2b0-4df3-8941-ca7d38acca1a

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "playbackKeyPairArn"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPlaybackKeyPair).__jsii_proxy_class__ = lambda : _IPlaybackKeyPairProxy


@jsii.interface(jsii_type="@aws-cdk/aws-ivs-alpha.IRecordingConfiguration")
class IRecordingConfiguration(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''(experimental) Represents the IVS Recording configuration.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="recordingConfigurationArn")
    def recording_configuration_arn(self) -> builtins.str:
        '''(experimental) The ARN of the Recording configuration.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="recordingConfigurationId")
    def recording_configuration_id(self) -> builtins.str:
        '''(experimental) The ID of the Recording configuration.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IRecordingConfigurationProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''(experimental) Represents the IVS Recording configuration.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-ivs-alpha.IRecordingConfiguration"

    @builtins.property
    @jsii.member(jsii_name="recordingConfigurationArn")
    def recording_configuration_arn(self) -> builtins.str:
        '''(experimental) The ARN of the Recording configuration.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "recordingConfigurationArn"))

    @builtins.property
    @jsii.member(jsii_name="recordingConfigurationId")
    def recording_configuration_id(self) -> builtins.str:
        '''(experimental) The ID of the Recording configuration.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "recordingConfigurationId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IRecordingConfiguration).__jsii_proxy_class__ = lambda : _IRecordingConfigurationProxy


@jsii.interface(jsii_type="@aws-cdk/aws-ivs-alpha.IStreamKey")
class IStreamKey(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''(experimental) Represents an IVS Stream Key.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="streamKeyArn")
    def stream_key_arn(self) -> builtins.str:
        '''(experimental) The stream-key ARN.

        For example: arn:aws:ivs:us-west-2:123456789012:stream-key/g1H2I3j4k5L6

        :stability: experimental
        :attribute: true
        '''
        ...


class _IStreamKeyProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''(experimental) Represents an IVS Stream Key.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-ivs-alpha.IStreamKey"

    @builtins.property
    @jsii.member(jsii_name="streamKeyArn")
    def stream_key_arn(self) -> builtins.str:
        '''(experimental) The stream-key ARN.

        For example: arn:aws:ivs:us-west-2:123456789012:stream-key/g1H2I3j4k5L6

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "streamKeyArn"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IStreamKey).__jsii_proxy_class__ = lambda : _IStreamKeyProxy


@jsii.enum(jsii_type="@aws-cdk/aws-ivs-alpha.LatencyMode")
class LatencyMode(enum.Enum):
    '''(experimental) Channel latency mode.

    :stability: experimental
    '''

    LOW = "LOW"
    '''(experimental) Use LOW to minimize broadcaster-to-viewer latency for interactive broadcasts.

    :stability: experimental
    '''
    NORMAL = "NORMAL"
    '''(experimental) Use NORMAL for broadcasts that do not require viewer interaction.

    :stability: experimental
    '''


@jsii.enum(jsii_type="@aws-cdk/aws-ivs-alpha.MaximumResolution")
class MaximumResolution(enum.Enum):
    '''(experimental) Maximum resolution for multitrack input.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        ivs.Channel(self, "ChannelWithMultitrackVideo",
            type=ivs.ChannelType.STANDARD,
            container_format=ivs.ContainerFormat.FRAGMENTED_MP4,
            multitrack_input_configuration=ivs.MultitrackInputConfiguration(
                maximum_resolution=ivs.MaximumResolution.HD,
                policy=ivs.Policy.ALLOW
            )
        )
    '''

    FULL_HD = "FULL_HD"
    '''(experimental) Full HD (1080p).

    :stability: experimental
    '''
    HD = "HD"
    '''(experimental) HD (720p).

    :stability: experimental
    '''
    SD = "SD"
    '''(experimental) SD (480p).

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-ivs-alpha.MultitrackInputConfiguration",
    jsii_struct_bases=[],
    name_mapping={"maximum_resolution": "maximumResolution", "policy": "policy"},
)
class MultitrackInputConfiguration:
    def __init__(
        self,
        *,
        maximum_resolution: MaximumResolution,
        policy: "Policy",
    ) -> None:
        '''(experimental) A complex type that specifies multitrack input configuration.

        :param maximum_resolution: (experimental) Maximum resolution for multitrack input.
        :param policy: (experimental) Indicates whether multitrack input is allowed or required.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            ivs.Channel(self, "ChannelWithMultitrackVideo",
                type=ivs.ChannelType.STANDARD,
                container_format=ivs.ContainerFormat.FRAGMENTED_MP4,
                multitrack_input_configuration=ivs.MultitrackInputConfiguration(
                    maximum_resolution=ivs.MaximumResolution.HD,
                    policy=ivs.Policy.ALLOW
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45e5ad260ecfc7dc92d23bd36a068b4a317871ab3322fe7e7ef92573084ea6b6)
            check_type(argname="argument maximum_resolution", value=maximum_resolution, expected_type=type_hints["maximum_resolution"])
            check_type(argname="argument policy", value=policy, expected_type=type_hints["policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "maximum_resolution": maximum_resolution,
            "policy": policy,
        }

    @builtins.property
    def maximum_resolution(self) -> MaximumResolution:
        '''(experimental) Maximum resolution for multitrack input.

        :stability: experimental
        '''
        result = self._values.get("maximum_resolution")
        assert result is not None, "Required property 'maximum_resolution' is missing"
        return typing.cast(MaximumResolution, result)

    @builtins.property
    def policy(self) -> "Policy":
        '''(experimental) Indicates whether multitrack input is allowed or required.

        :stability: experimental
        '''
        result = self._values.get("policy")
        assert result is not None, "Required property 'policy' is missing"
        return typing.cast("Policy", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MultitrackInputConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IPlaybackKeyPair)
class PlaybackKeyPair(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-ivs-alpha.PlaybackKeyPair",
):
    '''(experimental) A new IVS Playback Key Pair.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        key_pair = ivs.PlaybackKeyPair(self, "PlaybackKeyPair",
            public_key_material=my_public_key_pem_string
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        public_key_material: builtins.str,
        playback_key_pair_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param public_key_material: (experimental) The public portion of a customer-generated key pair.
        :param playback_key_pair_name: (experimental) An arbitrary string (a nickname) assigned to a playback key pair that helps the customer identify that resource. The value does not need to be unique. Default: Automatically generated name

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75931c57bc0ba240c98824ea65da9a0bc0a3bc48be2344ac7b70c03f259e632f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = PlaybackKeyPairProps(
            public_key_material=public_key_material,
            playback_key_pair_name=playback_key_pair_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="playbackKeyPairArn")
    def playback_key_pair_arn(self) -> builtins.str:
        '''(experimental) Key-pair ARN.

        For example: arn:aws:ivs:us-west-2:693991300569:playback-key/f99cde61-c2b0-4df3-8941-ca7d38acca1a

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "playbackKeyPairArn"))

    @builtins.property
    @jsii.member(jsii_name="playbackKeyPairFingerprint")
    def playback_key_pair_fingerprint(self) -> builtins.str:
        '''(experimental) Key-pair identifier.

        For example: 98:0d:1a:a0:19:96:1e:ea:0a:0a:2c:9a:42:19:2b:e7

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "playbackKeyPairFingerprint"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-ivs-alpha.PlaybackKeyPairProps",
    jsii_struct_bases=[],
    name_mapping={
        "public_key_material": "publicKeyMaterial",
        "playback_key_pair_name": "playbackKeyPairName",
    },
)
class PlaybackKeyPairProps:
    def __init__(
        self,
        *,
        public_key_material: builtins.str,
        playback_key_pair_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for creating a new Playback Key Pair.

        :param public_key_material: (experimental) The public portion of a customer-generated key pair.
        :param playback_key_pair_name: (experimental) An arbitrary string (a nickname) assigned to a playback key pair that helps the customer identify that resource. The value does not need to be unique. Default: Automatically generated name

        :stability: experimental
        :exampleMetadata: infused

        Example::

            key_pair = ivs.PlaybackKeyPair(self, "PlaybackKeyPair",
                public_key_material=my_public_key_pem_string
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f26b3314acb516329ef76511a5408ac87ae783446cab3f1be9ed1d0b81fa5b7)
            check_type(argname="argument public_key_material", value=public_key_material, expected_type=type_hints["public_key_material"])
            check_type(argname="argument playback_key_pair_name", value=playback_key_pair_name, expected_type=type_hints["playback_key_pair_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "public_key_material": public_key_material,
        }
        if playback_key_pair_name is not None:
            self._values["playback_key_pair_name"] = playback_key_pair_name

    @builtins.property
    def public_key_material(self) -> builtins.str:
        '''(experimental) The public portion of a customer-generated key pair.

        :stability: experimental
        '''
        result = self._values.get("public_key_material")
        assert result is not None, "Required property 'public_key_material' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def playback_key_pair_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) An arbitrary string (a nickname) assigned to a playback key pair that helps the customer identify that resource.

        The value does not need to be unique.

        :default: Automatically generated name

        :stability: experimental
        '''
        result = self._values.get("playback_key_pair_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PlaybackKeyPairProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-ivs-alpha.Policy")
class Policy(enum.Enum):
    '''(experimental) Whether multitrack input is allowed or required.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        ivs.Channel(self, "ChannelWithMultitrackVideo",
            type=ivs.ChannelType.STANDARD,
            container_format=ivs.ContainerFormat.FRAGMENTED_MP4,
            multitrack_input_configuration=ivs.MultitrackInputConfiguration(
                maximum_resolution=ivs.MaximumResolution.HD,
                policy=ivs.Policy.ALLOW
            )
        )
    '''

    ALLOW = "ALLOW"
    '''(experimental) Multitrack input is allowed.

    :stability: experimental
    '''
    REQUIRE = "REQUIRE"
    '''(experimental) Multitrack input is required.

    :stability: experimental
    '''


@jsii.enum(jsii_type="@aws-cdk/aws-ivs-alpha.Preset")
class Preset(enum.Enum):
    '''(experimental) An optional transcode preset for the channel.

    This is selectable only for ADVANCED_HD and ADVANCED_SD channel types.

    :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html
    :stability: experimental
    :exampleMetadata: infused

    Example::

        my_channel = ivs.Channel(self, "myChannel",
            type=ivs.ChannelType.ADVANCED_HD,
            preset=ivs.Preset.CONSTRAINED_BANDWIDTH_DELIVERY
        )
    '''

    CONSTRAINED_BANDWIDTH_DELIVERY = "CONSTRAINED_BANDWIDTH_DELIVERY"
    '''(experimental) Use a lower bitrate than STANDARD for each quality level.

    Use it if you have low download bandwidth and/or simple video content (e.g., talking heads).

    :stability: experimental
    '''
    HIGHER_BANDWIDTH_DELIVERY = "HIGHER_BANDWIDTH_DELIVERY"
    '''(experimental) Use a higher bitrate for each quality level.

    Use it if you have high download bandwidth and/or complex video content (e.g., flashes and quick scene changes).

    :stability: experimental
    '''


@jsii.implements(IRecordingConfiguration)
class RecordingConfiguration(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-ivs-alpha.RecordingConfiguration",
):
    '''(experimental) The IVS Recording configuration.

    :stability: experimental
    :resource: AWS::IVS::RecordingConfiguration
    :exampleMetadata: infused

    Example::

        # recording_bucket: s3.Bucket
        
        
        recording_configuration = ivs.RecordingConfiguration(self, "RecordingConfiguration",
            bucket=recording_bucket,
        
            # set rendition configuration
            rendition_configuration=ivs.RenditionConfiguration.custom([ivs.Resolution.HD, ivs.Resolution.SD])
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        recording_configuration_name: typing.Optional[builtins.str] = None,
        recording_reconnect_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        rendition_configuration: typing.Optional["RenditionConfiguration"] = None,
        thumbnail_configuration: typing.Optional["ThumbnailConfiguration"] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param bucket: (experimental) S3 bucket where recorded videos will be stored.
        :param recording_configuration_name: (experimental) The name of the Recording configuration. The value does not need to be unique. Default: - auto generate
        :param recording_reconnect_window: (experimental) If a broadcast disconnects and then reconnects within the specified interval, the multiple streams will be considered a single broadcast and merged together. ``recordingReconnectWindow`` must be between 0 and 300 seconds Default: - 0 seconds (means disabled)
        :param rendition_configuration: (experimental) A rendition configuration describes which renditions should be recorded for a stream. Default: - no rendition configuration
        :param thumbnail_configuration: (experimental) A thumbnail configuration enables/disables the recording of thumbnails for a live session and controls the interval at which thumbnails are generated for the live session. Default: - no thumbnail configuration

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84f7bfe030fdaeee83dd169a4320aa71fb0e576e76fac8a6fb5e799d638df503)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = RecordingConfigurationProps(
            bucket=bucket,
            recording_configuration_name=recording_configuration_name,
            recording_reconnect_window=recording_reconnect_window,
            rendition_configuration=rendition_configuration,
            thumbnail_configuration=thumbnail_configuration,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromArn")
    @builtins.classmethod
    def from_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        recording_configuration_arn: builtins.str,
    ) -> IRecordingConfiguration:
        '''(experimental) Imports an IVS Recording Configuration from its ARN.

        :param scope: -
        :param id: -
        :param recording_configuration_arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f6cbd063c6e695eed56d0c9c16dea95fe5f4b2a11e461c72cb33aa8d324e82d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument recording_configuration_arn", value=recording_configuration_arn, expected_type=type_hints["recording_configuration_arn"])
        return typing.cast(IRecordingConfiguration, jsii.sinvoke(cls, "fromArn", [scope, id, recording_configuration_arn]))

    @jsii.member(jsii_name="fromRecordingConfigurationId")
    @builtins.classmethod
    def from_recording_configuration_id(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        recording_configuration_id: builtins.str,
    ) -> IRecordingConfiguration:
        '''(experimental) Imports an IVS Recording Configuration from attributes.

        :param scope: -
        :param id: -
        :param recording_configuration_id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c05eebd5485c91c16b38e6bf9c1d896abb2eee019bb8f0da1ec7fa25b69b0d8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument recording_configuration_id", value=recording_configuration_id, expected_type=type_hints["recording_configuration_id"])
        return typing.cast(IRecordingConfiguration, jsii.sinvoke(cls, "fromRecordingConfigurationId", [scope, id, recording_configuration_id]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="recordingConfigurationArn")
    def recording_configuration_arn(self) -> builtins.str:
        '''(experimental) The ARN of the Recording configuration.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "recordingConfigurationArn"))

    @builtins.property
    @jsii.member(jsii_name="recordingConfigurationId")
    def recording_configuration_id(self) -> builtins.str:
        '''(experimental) The ID of the Recording configuration.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "recordingConfigurationId"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-ivs-alpha.RecordingConfigurationProps",
    jsii_struct_bases=[],
    name_mapping={
        "bucket": "bucket",
        "recording_configuration_name": "recordingConfigurationName",
        "recording_reconnect_window": "recordingReconnectWindow",
        "rendition_configuration": "renditionConfiguration",
        "thumbnail_configuration": "thumbnailConfiguration",
    },
)
class RecordingConfigurationProps:
    def __init__(
        self,
        *,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        recording_configuration_name: typing.Optional[builtins.str] = None,
        recording_reconnect_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        rendition_configuration: typing.Optional["RenditionConfiguration"] = None,
        thumbnail_configuration: typing.Optional["ThumbnailConfiguration"] = None,
    ) -> None:
        '''(experimental) Properties of the IVS Recording configuration.

        :param bucket: (experimental) S3 bucket where recorded videos will be stored.
        :param recording_configuration_name: (experimental) The name of the Recording configuration. The value does not need to be unique. Default: - auto generate
        :param recording_reconnect_window: (experimental) If a broadcast disconnects and then reconnects within the specified interval, the multiple streams will be considered a single broadcast and merged together. ``recordingReconnectWindow`` must be between 0 and 300 seconds Default: - 0 seconds (means disabled)
        :param rendition_configuration: (experimental) A rendition configuration describes which renditions should be recorded for a stream. Default: - no rendition configuration
        :param thumbnail_configuration: (experimental) A thumbnail configuration enables/disables the recording of thumbnails for a live session and controls the interval at which thumbnails are generated for the live session. Default: - no thumbnail configuration

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # recording_bucket: s3.Bucket
            
            
            recording_configuration = ivs.RecordingConfiguration(self, "RecordingConfiguration",
                bucket=recording_bucket,
            
                # set rendition configuration
                rendition_configuration=ivs.RenditionConfiguration.custom([ivs.Resolution.HD, ivs.Resolution.SD])
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21d80b5a61c717610ae7eec3eb729c41345980329354b0189415aab6624a4259)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument recording_configuration_name", value=recording_configuration_name, expected_type=type_hints["recording_configuration_name"])
            check_type(argname="argument recording_reconnect_window", value=recording_reconnect_window, expected_type=type_hints["recording_reconnect_window"])
            check_type(argname="argument rendition_configuration", value=rendition_configuration, expected_type=type_hints["rendition_configuration"])
            check_type(argname="argument thumbnail_configuration", value=thumbnail_configuration, expected_type=type_hints["thumbnail_configuration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket": bucket,
        }
        if recording_configuration_name is not None:
            self._values["recording_configuration_name"] = recording_configuration_name
        if recording_reconnect_window is not None:
            self._values["recording_reconnect_window"] = recording_reconnect_window
        if rendition_configuration is not None:
            self._values["rendition_configuration"] = rendition_configuration
        if thumbnail_configuration is not None:
            self._values["thumbnail_configuration"] = thumbnail_configuration

    @builtins.property
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''(experimental) S3 bucket where recorded videos will be stored.

        :stability: experimental
        '''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, result)

    @builtins.property
    def recording_configuration_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the Recording configuration.

        The value does not need to be unique.

        :default: - auto generate

        :stability: experimental
        '''
        result = self._values.get("recording_configuration_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def recording_reconnect_window(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) If a broadcast disconnects and then reconnects within the specified interval, the multiple streams will be considered a single broadcast and merged together.

        ``recordingReconnectWindow`` must be between 0 and 300 seconds

        :default: - 0 seconds (means disabled)

        :stability: experimental
        '''
        result = self._values.get("recording_reconnect_window")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def rendition_configuration(self) -> typing.Optional["RenditionConfiguration"]:
        '''(experimental) A rendition configuration describes which renditions should be recorded for a stream.

        :default: - no rendition configuration

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ivs-recordingconfiguration-renditionconfiguration.html
        :stability: experimental
        '''
        result = self._values.get("rendition_configuration")
        return typing.cast(typing.Optional["RenditionConfiguration"], result)

    @builtins.property
    def thumbnail_configuration(self) -> typing.Optional["ThumbnailConfiguration"]:
        '''(experimental) A thumbnail configuration enables/disables the recording of thumbnails for a live session and controls the interval at which thumbnails are generated for the live session.

        :default: - no thumbnail configuration

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ivs-recordingconfiguration-thumbnailconfiguration.html
        :stability: experimental
        '''
        result = self._values.get("thumbnail_configuration")
        return typing.cast(typing.Optional["ThumbnailConfiguration"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RecordingConfigurationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-ivs-alpha.RecordingMode")
class RecordingMode(enum.Enum):
    '''(experimental) Thumbnail recording mode.

    :stability: experimental
    '''

    INTERVAL = "INTERVAL"
    '''(experimental) Use INTERVAL to enable the generation of thumbnails for recorded video at a time interval controlled by the TargetIntervalSeconds property.

    :stability: experimental
    '''
    DISABLED = "DISABLED"
    '''(experimental) Use DISABLED to disable the generation of thumbnails for recorded video.

    :stability: experimental
    '''


class RenditionConfiguration(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-ivs-alpha.RenditionConfiguration",
):
    '''(experimental) Rendition configuration for IVS Recording configuration.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # recording_bucket: s3.Bucket
        
        
        recording_configuration = ivs.RecordingConfiguration(self, "RecordingConfiguration",
            bucket=recording_bucket,
        
            # set rendition configuration
            rendition_configuration=ivs.RenditionConfiguration.custom([ivs.Resolution.HD, ivs.Resolution.SD])
        )
    '''

    @jsii.member(jsii_name="all")
    @builtins.classmethod
    def all(cls) -> "RenditionConfiguration":
        '''(experimental) Record all available renditions.

        :stability: experimental
        '''
        return typing.cast("RenditionConfiguration", jsii.sinvoke(cls, "all", []))

    @jsii.member(jsii_name="custom")
    @builtins.classmethod
    def custom(
        cls,
        renditions: typing.Sequence["Resolution"],
    ) -> "RenditionConfiguration":
        '''(experimental) Record a subset of video renditions.

        :param renditions: A list of which renditions are recorded for a stream.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72cbe17572adb3a1344760dd6061eca45611a877ad41668210371524b85d90da)
            check_type(argname="argument renditions", value=renditions, expected_type=type_hints["renditions"])
        return typing.cast("RenditionConfiguration", jsii.sinvoke(cls, "custom", [renditions]))

    @jsii.member(jsii_name="none")
    @builtins.classmethod
    def none(cls) -> "RenditionConfiguration":
        '''(experimental) Does not record any video.

        :stability: experimental
        '''
        return typing.cast("RenditionConfiguration", jsii.sinvoke(cls, "none", []))

    @builtins.property
    @jsii.member(jsii_name="renditionSelection")
    def rendition_selection(self) -> "RenditionSelection":
        '''(experimental) The set of renditions are recorded for a stream.

        :stability: experimental
        '''
        return typing.cast("RenditionSelection", jsii.get(self, "renditionSelection"))

    @builtins.property
    @jsii.member(jsii_name="renditions")
    def renditions(self) -> typing.Optional[typing.List["Resolution"]]:
        '''(experimental) A list of which renditions are recorded for a stream.

        If you do not specify this property, no resolution is selected.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List["Resolution"]], jsii.get(self, "renditions"))


@jsii.enum(jsii_type="@aws-cdk/aws-ivs-alpha.RenditionSelection")
class RenditionSelection(enum.Enum):
    '''(experimental) Rendition selection mode.

    :stability: experimental
    '''

    ALL = "ALL"
    '''(experimental) Record all available renditions.

    :stability: experimental
    '''
    NONE = "NONE"
    '''(experimental) Does not record any video.

    This option is useful if you just want to record thumbnails.

    :stability: experimental
    '''
    CUSTOM = "CUSTOM"
    '''(experimental) Select a subset of video renditions to record.

    :stability: experimental
    '''


@jsii.enum(jsii_type="@aws-cdk/aws-ivs-alpha.Resolution")
class Resolution(enum.Enum):
    '''(experimental) Resolution for rendition.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # recording_bucket: s3.Bucket
        
        
        recording_configuration = ivs.RecordingConfiguration(self, "RecordingConfiguration",
            bucket=recording_bucket,
        
            # set rendition configuration
            rendition_configuration=ivs.RenditionConfiguration.custom([ivs.Resolution.HD, ivs.Resolution.SD])
        )
    '''

    FULL_HD = "FULL_HD"
    '''(experimental) Full HD (1080p).

    :stability: experimental
    '''
    HD = "HD"
    '''(experimental) HD (720p).

    :stability: experimental
    '''
    SD = "SD"
    '''(experimental) SD (480p).

    :stability: experimental
    '''
    LOWEST_RESOLUTION = "LOWEST_RESOLUTION"
    '''(experimental) Lowest resolution.

    :stability: experimental
    '''


@jsii.enum(jsii_type="@aws-cdk/aws-ivs-alpha.Storage")
class Storage(enum.Enum):
    '''(experimental) The format in which thumbnails are recorded for a stream.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # recording_bucket: s3.Bucket
        
        
        recording_configuration = ivs.RecordingConfiguration(self, "RecordingConfiguration",
            bucket=recording_bucket,
        
            # set thumbnail settings
            thumbnail_configuration=ivs.ThumbnailConfiguration.interval(ivs.Resolution.HD, [ivs.Storage.LATEST, ivs.Storage.SEQUENTIAL], Duration.seconds(30))
        )
    '''

    SEQUENTIAL = "SEQUENTIAL"
    '''(experimental) SEQUENTIAL records all generated thumbnails in a serial manner, to the media/thumbnails directory.

    :stability: experimental
    '''
    LATEST = "LATEST"
    '''(experimental) LATEST saves the latest thumbnail in media/thumbnails/latest/thumb.jpg and overwrites it at the interval specified by thumbnailTargetInterval.

    :stability: experimental
    '''


@jsii.implements(IStreamKey)
class StreamKey(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-ivs-alpha.StreamKey",
):
    '''(experimental) A new IVS Stream Key.

    :stability: experimental
    :exampleMetadata: fixture=with-channel infused

    Example::

        my_stream_key = my_channel.add_stream_key("StreamKey")
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        channel: IChannel,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param channel: (experimental) Channel ARN for the stream.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67fad0f56ffbc15680b0f651250d8bb5cf4dacb899e5c5bbf4abdcfc3ae39632)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = StreamKeyProps(channel=channel)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="streamKeyArn")
    def stream_key_arn(self) -> builtins.str:
        '''(experimental) The stream-key ARN.

        For example: arn:aws:ivs:us-west-2:123456789012:stream-key/g1H2I3j4k5L6

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "streamKeyArn"))

    @builtins.property
    @jsii.member(jsii_name="streamKeyValue")
    def stream_key_value(self) -> builtins.str:
        '''(experimental) The stream-key value.

        For example: sk_us-west-2_abcdABCDefgh_567890abcdef

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "streamKeyValue"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-ivs-alpha.StreamKeyProps",
    jsii_struct_bases=[],
    name_mapping={"channel": "channel"},
)
class StreamKeyProps:
    def __init__(self, *, channel: IChannel) -> None:
        '''(experimental) Properties for creating a new Stream Key.

        :param channel: (experimental) Channel ARN for the stream.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_ivs_alpha as ivs_alpha
            
            # channel: ivs_alpha.Channel
            
            stream_key_props = ivs_alpha.StreamKeyProps(
                channel=channel
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10474702d05a8d909166c4d0ef1de9632d82c17ae609436e3980c1bd4fa2ddb3)
            check_type(argname="argument channel", value=channel, expected_type=type_hints["channel"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "channel": channel,
        }

    @builtins.property
    def channel(self) -> IChannel:
        '''(experimental) Channel ARN for the stream.

        :stability: experimental
        '''
        result = self._values.get("channel")
        assert result is not None, "Required property 'channel' is missing"
        return typing.cast(IChannel, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamKeyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ThumbnailConfiguration(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-ivs-alpha.ThumbnailConfiguration",
):
    '''(experimental) Thumbnail configuration for IVS Recording configuration.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # recording_bucket: s3.Bucket
        
        
        recording_configuration = ivs.RecordingConfiguration(self, "RecordingConfiguration",
            bucket=recording_bucket,
        
            # set thumbnail settings
            thumbnail_configuration=ivs.ThumbnailConfiguration.interval(ivs.Resolution.HD, [ivs.Storage.LATEST, ivs.Storage.SEQUENTIAL], Duration.seconds(30))
        )
    '''

    @jsii.member(jsii_name="disable")
    @builtins.classmethod
    def disable(cls) -> "ThumbnailConfiguration":
        '''(experimental) Disable the generation of thumbnails for recorded video.

        :stability: experimental
        '''
        return typing.cast("ThumbnailConfiguration", jsii.sinvoke(cls, "disable", []))

    @jsii.member(jsii_name="interval")
    @builtins.classmethod
    def interval(
        cls,
        resolution: typing.Optional[Resolution] = None,
        storage: typing.Optional[typing.Sequence[Storage]] = None,
        target_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> "ThumbnailConfiguration":
        '''(experimental) Enable the generation of thumbnails for recorded video at a time interval.

        :param resolution: The desired resolution of recorded thumbnails for a stream. If you do not specify this property, same resolution as Input stream is used.
        :param storage: The format in which thumbnails are recorded for a stream. If you do not specify this property, ``ThumbnailStorage.SEQUENTIAL`` is set.
        :param target_interval: The targeted thumbnail-generation interval. If you do not specify this property, ``Duration.seconds(60)`` is set.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7613b92b71ccf7e94fae8fd523b44fd066922450801fcef8848b59ff75f9eeb2)
            check_type(argname="argument resolution", value=resolution, expected_type=type_hints["resolution"])
            check_type(argname="argument storage", value=storage, expected_type=type_hints["storage"])
            check_type(argname="argument target_interval", value=target_interval, expected_type=type_hints["target_interval"])
        return typing.cast("ThumbnailConfiguration", jsii.sinvoke(cls, "interval", [resolution, storage, target_interval]))

    @builtins.property
    @jsii.member(jsii_name="recordingMode")
    def recording_mode(self) -> typing.Optional[RecordingMode]:
        '''(experimental) Thumbnail recording mode.

        If you do not specify this property, ``ThumbnailRecordingMode.INTERVAL`` is set.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[RecordingMode], jsii.get(self, "recordingMode"))

    @builtins.property
    @jsii.member(jsii_name="resolution")
    def resolution(self) -> typing.Optional[Resolution]:
        '''(experimental) The desired resolution of recorded thumbnails for a stream.

        If you do not specify this property, same resolution as Input stream is used.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[Resolution], jsii.get(self, "resolution"))

    @builtins.property
    @jsii.member(jsii_name="storage")
    def storage(self) -> typing.Optional[typing.List[Storage]]:
        '''(experimental) The format in which thumbnails are recorded for a stream.

        If you do not specify this property, ``ThumbnailStorage.SEQUENTIAL`` is set.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[Storage]], jsii.get(self, "storage"))

    @builtins.property
    @jsii.member(jsii_name="targetInterval")
    def target_interval(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The targeted thumbnail-generation interval.

        Must be between 1 and 60 seconds. If you do not specify this property, ``Duration.seconds(60)`` is set.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], jsii.get(self, "targetInterval"))


@jsii.implements(IChannel)
class Channel(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-ivs-alpha.Channel",
):
    '''(experimental) A new IVS channel.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        my_rtmp_channel = ivs.Channel(self, "myRtmpChannel",
            type=ivs.ChannelType.STANDARD,
            insecure_ingest=True
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        authorized: typing.Optional[builtins.bool] = None,
        channel_name: typing.Optional[builtins.str] = None,
        container_format: typing.Optional[ContainerFormat] = None,
        insecure_ingest: typing.Optional[builtins.bool] = None,
        latency_mode: typing.Optional[LatencyMode] = None,
        multitrack_input_configuration: typing.Optional[typing.Union[MultitrackInputConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
        preset: typing.Optional[Preset] = None,
        recording_configuration: typing.Optional[IRecordingConfiguration] = None,
        type: typing.Optional[ChannelType] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param authorized: (experimental) Whether the channel is authorized. If you wish to make an authorized channel, you will need to ensure that a PlaybackKeyPair has been uploaded to your account as this is used to validate the signed JWT that is required for authorization Default: false
        :param channel_name: (experimental) A name for the channel. Default: Automatically generated name
        :param container_format: (experimental) Indicates which content-packaging format is used (MPEG-TS or fMP4). If ``multitrackInputConfiguration`` is specified, only fMP4 can be used. Otherwise, ``containerFormat`` may be set to ``ContainerFormat.TS`` or ``ContainerFormat.FRAGMENTED_MP4``. Default: - ``ContainerFormat.FRAGMENTED_MP4`` is automatically set when the ``multitrackInputConfiguration`` is specified. If not specified, it remains undefined and uses the IVS default setting (TS).
        :param insecure_ingest: (experimental) Whether the channel allows insecure RTMP ingest. Default: false
        :param latency_mode: (experimental) Channel latency mode. Default: LatencyMode.LOW
        :param multitrack_input_configuration: (experimental) Object specifying multitrack input configuration. You must specify ``multitrackInputConfiguration`` if you want to use MultiTrack Video. ``multitrackInputConfiguration`` is only supported for ``ChannelType.STANDARD``. Default: undefined - IVS default setting is not use MultiTrack Video.
        :param preset: (experimental) An optional transcode preset for the channel. Can be used for ADVANCED_HD and ADVANCED_SD channel types. When LOW or STANDARD is used, the preset will be overridden and set to none regardless of the value provided. Default: - Preset.HIGHER_BANDWIDTH_DELIVERY if channelType is ADVANCED_SD or ADVANCED_HD, none otherwise
        :param recording_configuration: (experimental) A recording configuration for the channel. Default: - recording is disabled
        :param type: (experimental) The channel type, which determines the allowable resolution and bitrate. If you exceed the allowable resolution or bitrate, the stream will disconnect immediately Default: ChannelType.STANDARD

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07139327925dc97a551bbf17c849a0f698e0c9c60d3da3f65f2b3d2bea0e0c50)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ChannelProps(
            authorized=authorized,
            channel_name=channel_name,
            container_format=container_format,
            insecure_ingest=insecure_ingest,
            latency_mode=latency_mode,
            multitrack_input_configuration=multitrack_input_configuration,
            preset=preset,
            recording_configuration=recording_configuration,
            type=type,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromChannelArn")
    @builtins.classmethod
    def from_channel_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        channel_arn: builtins.str,
    ) -> IChannel:
        '''(experimental) Import an existing channel.

        :param scope: -
        :param id: -
        :param channel_arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5efa416339cc500736f229c9a2b3b3b1143c18d7a26fe2712053e5511d370c5f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument channel_arn", value=channel_arn, expected_type=type_hints["channel_arn"])
        return typing.cast(IChannel, jsii.sinvoke(cls, "fromChannelArn", [scope, id, channel_arn]))

    @jsii.member(jsii_name="addStreamKey")
    def add_stream_key(self, id: builtins.str) -> StreamKey:
        '''(experimental) Adds a stream key for this IVS Channel.

        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65e1f25de7c3a0e391031082a65ee02865e1f85fe29f43a74bbc59866b95e50a)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(StreamKey, jsii.invoke(self, "addStreamKey", [id]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="channelArn")
    def channel_arn(self) -> builtins.str:
        '''(experimental) The channel ARN.

        For example: arn:aws:ivs:us-west-2:123456789012:channel/abcdABCDefgh

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "channelArn"))

    @builtins.property
    @jsii.member(jsii_name="channelIngestEndpoint")
    def channel_ingest_endpoint(self) -> builtins.str:
        '''(experimental) Channel ingest endpoint, part of the definition of an ingest server, used when you set up streaming software.

        For example: a1b2c3d4e5f6.global-contribute.live-video.net

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "channelIngestEndpoint"))

    @builtins.property
    @jsii.member(jsii_name="channelPlaybackUrl")
    def channel_playback_url(self) -> builtins.str:
        '''(experimental) Channel playback URL.

        For example:
        https://a1b2c3d4e5f6.us-west-2.playback.live-video.net/api/video/v1/us-west-2.123456789012.channel.abcdEFGH.m3u8

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "channelPlaybackUrl"))


__all__ = [
    "Channel",
    "ChannelProps",
    "ChannelType",
    "ContainerFormat",
    "IChannel",
    "IPlaybackKeyPair",
    "IRecordingConfiguration",
    "IStreamKey",
    "LatencyMode",
    "MaximumResolution",
    "MultitrackInputConfiguration",
    "PlaybackKeyPair",
    "PlaybackKeyPairProps",
    "Policy",
    "Preset",
    "RecordingConfiguration",
    "RecordingConfigurationProps",
    "RecordingMode",
    "RenditionConfiguration",
    "RenditionSelection",
    "Resolution",
    "Storage",
    "StreamKey",
    "StreamKeyProps",
    "ThumbnailConfiguration",
]

publication.publish()

def _typecheckingstub__0ebf6a0e98bbd5b88d9676fbe616666a44f837cba80675eade5df1fea22c9d22(
    *,
    authorized: typing.Optional[builtins.bool] = None,
    channel_name: typing.Optional[builtins.str] = None,
    container_format: typing.Optional[ContainerFormat] = None,
    insecure_ingest: typing.Optional[builtins.bool] = None,
    latency_mode: typing.Optional[LatencyMode] = None,
    multitrack_input_configuration: typing.Optional[typing.Union[MultitrackInputConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    preset: typing.Optional[Preset] = None,
    recording_configuration: typing.Optional[IRecordingConfiguration] = None,
    type: typing.Optional[ChannelType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__809e7d60e77d2ede718027f4d99dcf810db3b33f39daebb557b424c6457e2f22(
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45e5ad260ecfc7dc92d23bd36a068b4a317871ab3322fe7e7ef92573084ea6b6(
    *,
    maximum_resolution: MaximumResolution,
    policy: Policy,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75931c57bc0ba240c98824ea65da9a0bc0a3bc48be2344ac7b70c03f259e632f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    public_key_material: builtins.str,
    playback_key_pair_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f26b3314acb516329ef76511a5408ac87ae783446cab3f1be9ed1d0b81fa5b7(
    *,
    public_key_material: builtins.str,
    playback_key_pair_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84f7bfe030fdaeee83dd169a4320aa71fb0e576e76fac8a6fb5e799d638df503(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    recording_configuration_name: typing.Optional[builtins.str] = None,
    recording_reconnect_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    rendition_configuration: typing.Optional[RenditionConfiguration] = None,
    thumbnail_configuration: typing.Optional[ThumbnailConfiguration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f6cbd063c6e695eed56d0c9c16dea95fe5f4b2a11e461c72cb33aa8d324e82d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    recording_configuration_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c05eebd5485c91c16b38e6bf9c1d896abb2eee019bb8f0da1ec7fa25b69b0d8(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    recording_configuration_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21d80b5a61c717610ae7eec3eb729c41345980329354b0189415aab6624a4259(
    *,
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    recording_configuration_name: typing.Optional[builtins.str] = None,
    recording_reconnect_window: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    rendition_configuration: typing.Optional[RenditionConfiguration] = None,
    thumbnail_configuration: typing.Optional[ThumbnailConfiguration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72cbe17572adb3a1344760dd6061eca45611a877ad41668210371524b85d90da(
    renditions: typing.Sequence[Resolution],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67fad0f56ffbc15680b0f651250d8bb5cf4dacb899e5c5bbf4abdcfc3ae39632(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    channel: IChannel,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10474702d05a8d909166c4d0ef1de9632d82c17ae609436e3980c1bd4fa2ddb3(
    *,
    channel: IChannel,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7613b92b71ccf7e94fae8fd523b44fd066922450801fcef8848b59ff75f9eeb2(
    resolution: typing.Optional[Resolution] = None,
    storage: typing.Optional[typing.Sequence[Storage]] = None,
    target_interval: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07139327925dc97a551bbf17c849a0f698e0c9c60d3da3f65f2b3d2bea0e0c50(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    authorized: typing.Optional[builtins.bool] = None,
    channel_name: typing.Optional[builtins.str] = None,
    container_format: typing.Optional[ContainerFormat] = None,
    insecure_ingest: typing.Optional[builtins.bool] = None,
    latency_mode: typing.Optional[LatencyMode] = None,
    multitrack_input_configuration: typing.Optional[typing.Union[MultitrackInputConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    preset: typing.Optional[Preset] = None,
    recording_configuration: typing.Optional[IRecordingConfiguration] = None,
    type: typing.Optional[ChannelType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5efa416339cc500736f229c9a2b3b3b1143c18d7a26fe2712053e5511d370c5f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    channel_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65e1f25de7c3a0e391031082a65ee02865e1f85fe29f43a74bbc59866b95e50a(
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
