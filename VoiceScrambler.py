import hashlib
import wave
import argparse
from Crypto import Random
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
import hashlib


def parseArgs():
    argParser = argparse.ArgumentParser()
    argParser.add_argument("--encrypt", action='store_true', help='Encrypt a provided .wav file...')
    argParser.add_argument("--decrypt", action='store_true', help='Decrypt a provided .wav file...')
    argParser.add_argument("--audio", type=str, help="Path to the .wav audio file to be processed.")
    argParser.add_argument("--swav", type=str, help="Path to save the processed .wav file")
    argParser.add_argument("--password", type=str, help="Password that should be used to encrypt or decrypt the audio")
    return argParser.parse_args()


def outError(msg):
    print("[ERROR] :   " + msg)


def desEncryptBytes(key, byteData):
    lenBytes = bytearray(int(len(byteData)).to_bytes(4, byteorder='big'))
    byteData = lenBytes + byteData
    key = hashlib.sha256(key).digest()[0:8]
    desInst = DES.new(bytes(key), DES.MODE_ECB)
    return desInst.encrypt(pad(byteData, 16))


def desDecryptBytes(key, byteData):
    key = hashlib.sha256(key).digest()[0:8]
    desInst = DES.new(key, DES.MODE_ECB)
    dec = desInst.decrypt(pad(byteData, 16))
    decSz = dec[0:4]
    return dec[4:int.from_bytes(decSz, byteorder='big') + 4]


# def encryptFrames(frmArr):
# aesInst = AESCrypto.AesCrypto(cmdLine.password,
#                              [0x15, 0xa2, 0xcd, 0xae, 0x5d, 0x9a, 0x3c, 0x5f, 0x8b, 0xc5, 0xa3, 0xaf, 0xda, 0x5c,
#                                 0x9f, 0x4d])
#   return aesInst.aesEncrypt(frmArr)


# def decryptFrames(frmArr):
#   aesInst = AESCrypto.AesCrypto(cmdLine.password,
#                                [0x15, 0xa2, 0xcd, 0xae, 0x5d, 0x9a, 0x3c, 0x5f, 0x8b, 0xc5, 0xa3, 0xaf, 0xda, 0x5c,
#                                0x9f, 0x4d])
# return aesInst.aesDecrypt(frmArr)


def processFrames(cmdParams):
    if cmdParams.audio is None:
        outError("Please provide the required .wav file to be processed.")
        return
    audioHandle = wave.open(cmdParams.audio, 'rb')
    frmCount = audioHandle.getnframes()
    frmBytes = bytearray(audioHandle.readframes(frmCount))
    return [frmCount, frmBytes, audioHandle.getparams(), audioHandle.getnchannels()]


def writeOut(cmdParams, frmBytes, frmChannels, frmParams):
    outAudio = wave.open(cmdParams.swav, 'wb')
    outAudio.setparams(frmParams)
    outAudio.setnchannels(frmChannels)
    outAudio.writeframes(frmBytes)
    outAudio.close()


if __name__ == "__main__":
    cmdLine = parseArgs()

    if cmdLine.encrypt is None and cmdLine.decrypt is None:
        outError("Please provide an operation to perform...")
        exit(-1)

    if cmdLine.audio is None or cmdLine.swav is None or cmdLine.password is None:
        outError("Please provide the required arguments to perform the requested operations...")
        exit(-1)

    audioFrm = processFrames(cmdLine)
    if cmdLine.encrypt:
        encryptedFrm = desEncryptBytes(cmdLine.password.encode(), audioFrm[1])
        writeOut(cmdLine, encryptedFrm, audioFrm[3], audioFrm[2])
    else:
        decryptedFrm = desDecryptBytes(cmdLine.password.encode(), audioFrm[1])
        writeOut(cmdLine, decryptedFrm, audioFrm[3], audioFrm[2])

    # if cmdLine.encrypt:
    # encryptedFrm = encryptFrames(audioFrm[1])
    # writeOut(cmdLine, encryptedFrm, audioFrm[3], audioFrm[2])
    # elif cmdLine.decrypt:
    # decryptFrames(audioFrm[1])
    # else:
    #   outError("Just do it right next time...")
