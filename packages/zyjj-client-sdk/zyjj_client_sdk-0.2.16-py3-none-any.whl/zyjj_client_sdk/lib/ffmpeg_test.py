from zyjj_client_sdk.lib.ffmpeg import FFMpegService

service = FFMpegService()


def test_get_duration():
    # print(service.get_duration("/Users/xiaoyou/code/zyjj/zyjj-client-lab/tmp/test.mp3"))
    print(service.ffmpeg_run("-i /tmp/d6f32566-d1f9-45e9-a808-a1a63b7b19e2.jpg -q 5 -vf \"scale='if(gt(iw,4000),4000,iw)':'if(gt(ih*4000/iw,ih),ih,ih*4000/iw)'\" /tmp/5a52146d-b8ba-452f-b8d1-66da8e41202e.jpg"))

