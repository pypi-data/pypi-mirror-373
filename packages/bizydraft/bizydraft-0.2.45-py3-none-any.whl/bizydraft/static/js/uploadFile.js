import { getCookie } from './tool.js';
export async function fileToOss(file) {
  try {

    // 检查token是否存在
    const apiHost = 'https://bizyair.cn/api'
    // const apiHost = 'http://localhost:3000/api'
    const authToken = getCookie('bizy_token')
    // console.log(authToken)
    if (!authToken) {
      throw new Error('未找到认证Token，请先登录');
    }

    // 获取上传凭证
    const uploadToken = await fetch(`${apiHost}/special/community/upload_token?file_name=${encodeURIComponent(file.name)}&file_type=inputs`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      }
    });

    // 检查响应状态
    if (!uploadToken.ok) {
      const errorText = await uploadToken.text();
      console.error('获取上传凭证失败:', uploadToken.status, errorText);
      throw new Error(`获取上传凭证失败: ${uploadToken.status} ${uploadToken.statusText}`);
    }

    const {data} = await uploadToken.json();
    // console.log('上传凭证响应:', data);

    // 使用STS凭证上传
    const ossConfig = {
      accessKeyId: data.data.file.access_key_id,
      accessKeySecret: data.data.file.access_key_secret,
      securityToken: data.data.file.security_token,
      bucket: data.data.storage.bucket,
      region: data.data.storage.region,
      objectKey: data.data.file.object_key
    };

    // console.log('OSS配置:', ossConfig);

    // 改用官方推荐的表单上传方式
    const formData = new FormData();

    // 构建Policy
    const expiration = new Date();
    expiration.setHours(expiration.getHours() + 1); // Policy过期时间1小时

    const policyObj = {
      expiration: expiration.toISOString(),
      conditions: [
        // 文件大小限制
        ['content-length-range', 0, 1048576000], // 最大1000MB
        // 指定允许的文件名前缀
        ['starts-with', '$key', ossConfig.objectKey.split('/')[0]]
      ]
    };

    // Policy Base64编码
    const policy = btoa(JSON.stringify(policyObj));
    // console.log('Policy:', policy);

    // 构建表单字段
    formData.append('key', ossConfig.objectKey);
    formData.append('OSSAccessKeyId', ossConfig.accessKeyId);
    formData.append('policy', policy);
    formData.append('success_action_status', '200');

    // 如果有临时token，需要添加
    if (ossConfig.securityToken) {
      formData.append('x-oss-security-token', ossConfig.securityToken);
    }

    // 计算签名 - 阿里云官方要求使用HMAC-SHA1
    const signature = await hmacSha1(policy, ossConfig.accessKeySecret);
    // console.log('计算的签名:', signature);
    formData.append('signature', signature);

    // 最后添加文件内容
    formData.append('file', file);

    // OSS服务端点
    const host = `https://${ossConfig.bucket}.${ossConfig.region}.aliyuncs.com`;
    // console.log('上传地址:', host);

    // 开始上传
    const uploadResponse = await fetch(host, {
      method: 'POST',
      body: formData
    });

    // 检查响应
    if (!uploadResponse.ok) {
      const errorText = await uploadResponse.text();
      console.error('上传失败:', uploadResponse.status, errorText);
      throw new Error(`上传失败: ${uploadResponse.status} ${uploadResponse.statusText}`);
    }

    // 构建公开访问URL
    const fileUrl = `${host}/${ossConfig.objectKey}`;

    // 提交资源
    await fetch(`${apiHost}/special/community/commit_input_resource`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify({
        object_key: data.data.file.object_key,
        name: file.name,
      })
    })
    return {
      url: fileUrl,
      ossTokenFile: data.data.file,
      ossTokenStorage: data.data.storage
    };
  } catch (error) {
    console.error('文件上传到OSS失败:', error);

    throw error;
  }
}

// 使用标准的HMAC-SHA1签名算法
async function hmacSha1(message, key) {
  // 使用浏览器原生的SubtleCrypto API
  const encoder = new TextEncoder();
  const keyData = encoder.encode(key);
  const messageData = encoder.encode(message);

  // 导入密钥
  const cryptoKey = await window.crypto.subtle.importKey(
    'raw',
    keyData,
    { name: 'HMAC', hash: 'SHA-1' },
    false,
    ['sign']
  );

  // 计算签名
  const signature = await window.crypto.subtle.sign(
    'HMAC',
    cryptoKey,
    messageData
  );

  // 转换为Base64编码
  const base64Signature = arrayBufferToBase64(signature);
  return base64Signature;
}

// 将ArrayBuffer转换为Base64字符串
function arrayBufferToBase64(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}
