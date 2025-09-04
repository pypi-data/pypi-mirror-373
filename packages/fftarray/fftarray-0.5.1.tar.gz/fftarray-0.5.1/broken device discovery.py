# info = xp.__array_namespace_info__()
# devices = info.devices()
# # jax returns "None" because arrays can be uncommitted.
# # see https://github.com/jax-ml/jax/issues/27606
# # But we want to actually compare the resulting device so
# # we take this method instead.
# default_device = array_api_compat.device(xp.empty(1))
# assert len(devices) > 0
# res = [
#     (xp, None, default_device)
# ]
# if len(devices) > 1:
#     for dev in devices:
#         if dev != default_device and dev is not None:
#             res.append(
#                 (xp, dev, dev),
#             )
#             break
# return res